import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.utils.api_tracker import SimpleTavilyClient
from app.core.utils import extract_json_from_response, truncate_search_results
from app.core.prompts import format_customer_insights_analysis_prompt
from app.core.config import get_logger
from app.services.progress_tracker import progress_tracker

logger = get_logger(__name__)

class CustomerInsightsAgent:

    def __init__(self, openai_api_key: str, tavily_api_key: str):
        from app.core.ai_client import get_llm_client
        self.llm = get_llm_client(openai_api_key)
        self.tavily_api_key = tavily_api_key
    
    async def analyze_customer_insights(
        self,
        query: str,
        context: Dict[str, Any],
        request_id: str = "unknown"
    ) -> Dict[str, Any]:
        
        try:
            search_results = await self._search_customer_data(
                query, context, request_id
            )
            
            analysis = await self._analyze_customer_data(
                context, search_results, request_id
            )
            
            result = {
                "agent_name": "CustomerInsightsAgent",
                "status": "success",
                "analysis": analysis,
                "sources_analyzed": len(search_results),
                "data_sources": {
                    "feedback_sources_count": len(search_results),
                    "source_urls": [result.get("url", "") for result in search_results[:10]],
                    "search_query": query,
                    "analysis_method": "LangGraph-enhanced customer insights analysis"
                },
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "sector": context.get("sector", ""),
                    "product_idea": context.get("product_idea", ""),
                    "research_depth": context.get("research_depth", "standard")
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"[{request_id}] CustomerInsightsAgent: Analysis failed - {e}")
            return self._create_error_result(context, str(e))
    
    async def _search_customer_data(
        self, 
        query: str, 
        context: Dict[str, Any], 
        request_id: str
    ) -> List[Dict[str, Any]]:
        try:
            tavily_client = SimpleTavilyClient(request_id)
            
            research_depth = context.get("research_depth", "standard")
            max_sources = context.get("max_sources", 20)
            
            search_depth = "advanced" if research_depth in ["standard", "comprehensive"] else "basic"
            
            # Checkpoint: Customer search started
            progress_tracker.complete_checkpoint(request_id, "customer_search_started")
            
            search_response = tavily_client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_sources,
                include_answer=True,
                include_raw_content=False
            )
            
            search_results = search_response.get("results", [])
            
            # Only record checkpoint if search was successful
            if search_results:
                progress_tracker.complete_checkpoint(request_id, "customer_search_completed")
            
            urls_to_extract, extract_depth = self._determine_extraction_params(
                search_results, research_depth
            )
            
            if urls_to_extract:
                extract_response = tavily_client.extract(
                    urls=urls_to_extract, 
                    extract_depth=extract_depth
                )
                extracted_data = extract_response.get("results", [])
                
                # Only record checkpoint if extraction was successful
                if extracted_data:
                    progress_tracker.complete_checkpoint(request_id, "customer_extraction_completed")
                
                for i, result in enumerate(search_results[:len(extracted_data)]):
                    if i < len(extracted_data):
                        result["extracted_content"] = extracted_data[i].get("raw_content", "")
            
            return search_results
            
        except Exception as e:
            logger.error(f"[{request_id}] CustomerInsightsAgent: Search failed - {e}")
            return []
    
    def _determine_extraction_params(
        self, 
        search_results: List[Dict], 
        research_depth: str
    ) -> tuple[List[str], str]:
        if research_depth == "basic":
            urls = [result["url"] for result in search_results[:5]]
            depth = "basic"
        elif research_depth == "standard":
            urls = [result["url"] for result in search_results[:5]]
            depth = "advanced"
        else:  # comprehensive
            urls = [result["url"] for result in search_results[:10]]
            depth = "advanced"
        
        return urls, depth
    
    async def _analyze_customer_data(
        self,
        context: Dict[str, Any],
        search_results: List[Dict[str, Any]],
        request_id: str
    ) -> Dict[str, Any]:
        try:
            product_idea = context.get("product_idea", "")
            sector = context.get("sector", "")
            
            
            # Truncate search results to fit within token limits
            truncated_results = truncate_search_results(search_results)
            customer_data = self._prepare_data_for_analysis(truncated_results, request_id)
            
            system_prompt, human_prompt = format_customer_insights_analysis_prompt(
                product_idea, sector, json.dumps(customer_data, indent=2)
            )
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ])
            
            json_content = extract_json_from_response(response.content)
            analysis = json.loads(json_content)
            
            # Only record checkpoint if analysis was successful
            if analysis and not analysis.get("error"):
                progress_tracker.complete_checkpoint(request_id, "customer_analysis_completed")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"[{request_id}] CustomerInsightsAgent: JSON parsing failed - {e}")
            return self._create_error_analysis(f"JSON parsing error: {str(e)}")
            
        except Exception as e:
            logger.error(f"[{request_id}] CustomerInsightsAgent: Analysis failed - {e}")
            return self._create_error_analysis(str(e))
    
    def _prepare_data_for_analysis(self, search_results: List[Dict[str, Any]], request_id: str = "unknown") -> List[Dict[str, str]]:
        filtered_results = []
        for result in search_results:
            content = result.get("content", "")
            extracted_content = result.get("extracted_content", "")
            
            # Remove content truncation to allow full data flow
            
            filtered_results.append({
                "title": result.get("title", ""),
                "content": content,
                "extracted_content": extracted_content,
                "url": result.get("url", "")
            })
        return filtered_results
    
    def _create_error_analysis(self, error_msg: str) -> Dict[str, Any]:
        return {
            "pain_points": [{
                "issue": f"Analysis error: {error_msg}", 
                "frequency": "Unknown", 
                "impact": "Unknown", 
                "description": "Error in data processing"
            }],
            "unmet_needs": ["Unable to analyze"],
            "satisfaction_drivers": ["Error occurred"],
            "common_complaints": ["Analysis failed"],
            "feature_requests": ["Unable to identify"],
            "customer_sentiment": {"positive": [], "negative": ["Error"], "neutral": []},
            "user_personas": ["Unable to identify"],
            "improvement_opportunities": ["Analysis failed - please retry"],
            "key_insights": ["System error occurred"]
        }
    
    def _create_error_result(self, context: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        return {
            "agent_name": "CustomerInsightsAgent",
            "status": "error",
            "error": error_msg,
            "analysis": self._create_error_analysis(error_msg),
            "sources_analyzed": 0,
            "data_sources": {
                "feedback_sources_count": 0,
                "source_urls": [],
                "search_query": "",
                "analysis_method": "Error occurred"
            },
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
