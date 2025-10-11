import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.db.redis_manager import redis_manager

logger = logging.getLogger(__name__)

class SearchService:
    
    def __init__(self):
        self.search_index_key = "research_tasks:search_index"
        self.task_data_prefix = "research_task:"
    
    async def index_task(self, task: Dict[str, Any]) -> bool:
        redis_client = redis_manager.get_client()
        if not redis_client:
            return False
        
        try:
            request_id = task.get("request_id")
            if not request_id:
                return False
            
            search_text = self._create_search_text(task)
            task_data = self._prepare_task_data(task, search_text)
            
            task_key = f"{self.task_data_prefix}{request_id}"
            await redis_client.hset(task_key, mapping=task_data)
            
            score = datetime.now().timestamp()
            await redis_client.zadd(self.search_index_key, {request_id: score})
            
            return True
            
        except Exception as e:
            logger.error(f"Error indexing task {task.get('request_id')}: {e}")
            return False
    
    def _create_search_text(self, task: Dict[str, Any]) -> str:
        search_parts = [
            task.get("product_idea", ""),  # Changed from "query" to "product_idea"
            task.get("status", ""),
        ]
        
        if task.get("result") and task["result"].get("final_report"):
            report = task["result"]["final_report"]
            if report.get("synthesis"):
                search_parts.extend(self._extract_synthesis_text(report["synthesis"]))
        
        return " ".join(filter(None, search_parts)).lower()
    
    def _extract_synthesis_text(self, synthesis: Dict[str, Any]) -> List[str]:
        parts = [
            synthesis.get("executive_summary", ""),
            " ".join(synthesis.get("actionable_recommendations", [])),
            " ".join([
                insight.get("insight", "")
                for insight in synthesis.get("key_insights", [])
            ])
        ]
        return parts
    
    def _prepare_task_data(self, task: Dict[str, Any], search_text: str) -> Dict[str, str]:
        return {
            "request_id": task.get("request_id", ""),
            "query": task.get("product_idea", ""),  # Changed from "query" to "product_idea"
            "status": task.get("status", ""),
            "started_at": task.get("started_at", ""),
            "completed_at": task.get("completed_at", ""),
            "search_text": search_text,
            "indexed_at": datetime.now().isoformat()
        }
    
    async def search_tasks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        redis_client = redis_manager.get_client()
        if not redis_client or not query.strip():
            return []
        
        try:
            query_lower = query.lower().strip()
            results = []
            
            task_ids = await redis_client.zrevrange(self.search_index_key, 0, -1)
            
            for task_id in task_ids:
                if len(results) >= limit:
                    break
                
                task_data = await self._get_task_data(redis_client, task_id)
                if not task_data:
                    continue
                
                search_text = task_data.get("search_text", "")
                if query_lower in search_text:
                    result = self._create_search_result(task_data, query_lower)
                    results.append(result)
            
            results.sort(key=lambda x: (x["relevance"], x.get("started_at", "")), reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Error searching tasks: {e}")
            return []
    
    async def _get_task_data(self, redis_client, task_id: str) -> Optional[Dict[str, str]]:
        task_key = f"{self.task_data_prefix}{task_id}"
        return await redis_client.hgetall(task_key)
    
    def _create_search_result(self, task_data: Dict[str, str], query: str) -> Dict[str, Any]:
        search_text = task_data.get("search_text", "")
        
        query_words = query.split()
        matches = sum(1 for word in query_words if word in search_text)
        relevance = matches / len(query_words) if query_words else 0
        
        return {
            "request_id": task_data.get("request_id"),
            "query": task_data.get("query"),
            "status": task_data.get("status"),
            "started_at": task_data.get("started_at"),
            "completed_at": task_data.get("completed_at"),
            "relevance": relevance,
            "match_preview": self._create_match_preview(task_data.get("query", ""), query)
        }
    
    def _create_match_preview(self, text: str, query: str) -> str:
        if not text or not query:
            return text[:100] + "..." if len(text) > 100 else text
        
        text_lower = text.lower()
        index = text_lower.find(query.lower())
        
        if index == -1:
            return text[:100] + "..." if len(text) > 100 else text
        
        start = max(0, index - 30)
        end = min(len(text), index + len(query) + 30)
        preview = text[start:end]
        
        if start > 0:
            preview = "..." + preview
        if end < len(text):
            preview = preview + "..."
        
        return preview
    
    async def remove_task(self, request_id: str) -> bool:
        redis_client = redis_manager.get_client()
        if not redis_client:
            return False
        
        try:
            await redis_client.zrem(self.search_index_key, request_id)
            
            task_key = f"{self.task_data_prefix}{request_id}"
            await redis_client.delete(task_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing task {request_id}: {e}")
            return False
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        redis_client = redis_manager.get_client()
        if not redis_client or not partial_query.strip():
            return []
        
        try:
            suggestions = []
            partial_lower = partial_query.lower().strip()
            
            # Limit the number of task IDs we fetch to improve performance
            # Only get the most recent 50 tasks instead of all
            task_ids = await redis_client.zrevrange(self.search_index_key, 0, 49)
            
            for task_id in task_ids:
                if len(suggestions) >= limit:
                    break
                
                task_data = await self._get_task_data(redis_client, task_id)
                if not task_data:
                    continue
                
                query = task_data.get("query", "")
                if not query:
                    continue
                
                match_type = self._get_match_type(query, partial_lower)
                if match_type:
                    suggestions.append({
                        "query": query,
                        "request_id": task_data.get("request_id"),
                        "status": task_data.get("status"),
                        "started_at": task_data.get("started_at"),
                        "match_type": match_type
                    })
            
            suggestions.sort(key=lambda x: (
                0 if x["match_type"] == "word_start" else 1,
                -self._parse_timestamp(x.get("started_at", ""))
            ))
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []
    
    def _get_match_type(self, query: str, partial_query: str) -> Optional[str]:
        query_lower = query.lower()
        words = query_lower.split()
        
        for word in words:
            if word.startswith(partial_query):
                return "word_start"
        
        if partial_query in query_lower:
            return "contains"
        
        return None
    
    def _parse_timestamp(self, timestamp: str) -> float:
        try:
            cleaned = timestamp.replace("-", "").replace(":", "").replace("T", "").replace("Z", "")
            return float(cleaned[:14])
        except Exception:
            return 0.0

search_service = SearchService()
