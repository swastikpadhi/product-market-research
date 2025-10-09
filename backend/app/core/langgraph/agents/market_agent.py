import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.utils.api_tracker import SimpleTavilyClient
from app.core.utils import extract_json_from_response
from app.core.prompts import format_market_analyzer_analysis_prompt
from app.core.config import get_logger
from app.services.progress_tracker import progress_tracker

logger = get_logger(__name__)

class MarketAnalysisAgent:
    
    def __init__(self, openai_api_key: str, tavily_api_key: str):
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key, temperature=0.1)
        self.tavily_api_key = tavily_api_key
    
    async def analyze_market_trends(
        self, query: str, context: Dict[str, Any], request_id: str = "unknown"
    ) -> Dict[str, Any]:
        try:
            search_results = await self._search_market_data(query, context, request_id)
            analysis = await self._analyze_market_data(context, search_results, request_id)
            
            result = {
                "agent_name": "MarketAnalysisAgent",
                "status": "success",
                "analysis": analysis,
                "sources_analyzed": len(search_results),
                "data_sources": {
                    "market_data_sources_count": len(search_results),
                    "source_urls": [result.get("url", "") for result in search_results[:10]],
                    "search_query": query,
                    "analysis_method": "LangGraph-enhanced market trends analysis"
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
            logger.error(f"[{request_id}] MarketAnalysisAgent: Analysis failed - {e}")
            return self._create_error_result(context, str(e))
    
    async def _search_market_data(
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
            
            # Checkpoint: Market search started
            await progress_tracker.complete_checkpoint(request_id, "market_search_started")
            
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
                await progress_tracker.complete_checkpoint(request_id, "market_search_completed")
            
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
                    await progress_tracker.complete_checkpoint(request_id, "market_extraction_completed")
                
                for i, result in enumerate(search_results[:len(extracted_data)]):
                    if i < len(extracted_data):
                        result["extracted_content"] = extracted_data[i].get("raw_content", "")
            
            return search_results
            
        except Exception as e:
            logger.error(f"[{request_id}] MarketAnalysisAgent: Search failed - {e}")
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
    
    async def _analyze_market_data(
        self,
        context: Dict[str, Any],
        search_results: List[Dict[str, Any]],
        request_id: str
    ) -> Dict[str, Any]:
        try:
            product_idea = context.get("product_idea", "")
            sector = context.get("sector", "")
            
            market_data = self._prepare_data_for_analysis(search_results, request_id)
            
            system_prompt, human_prompt = format_market_analyzer_analysis_prompt(
                product_idea, sector, json.dumps(market_data, indent=2)
            )
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ])
            
            json_content = extract_json_from_response(response.content)
            analysis = json.loads(json_content)
            
            # Only record checkpoint if analysis was successful
            if analysis and not analysis.get("error"):
                await progress_tracker.complete_checkpoint(request_id, "market_analysis_completed")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"[{request_id}] MarketAnalysisAgent: JSON parsing failed - {e}")
            return self._create_error_analysis(f"JSON parsing error: {str(e)}")
            
        except Exception as e:
            logger.error(f"[{request_id}] MarketAnalysisAgent: Analysis failed - {e}")
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
            "market_size": {"current": "Error", "projected": "Error"},
            "growth_rate": "Error",
            "key_trends": [f"Analysis error: {error_msg}"],
            "drivers": ["Error in data processing"],
            "challenges": ["System error occurred"],
            "opportunities": ["Unable to analyze"],
            "regulatory_landscape": "Error occurred during analysis",
            "technology_impact": "Error",
            "future_outlook": "Error",
            "key_insights": ["Analysis failed - please retry"]
        }
    
    def _create_error_result(self, context: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        return {
            "agent_name": "MarketAnalysisAgent",
            "status": "error",
            "error": error_msg,
            "analysis": self._create_error_analysis(error_msg),
            "sources_analyzed": 0,
            "data_sources": {
                "market_data_sources_count": 0,
                "source_urls": [],
                "search_query": "",
                "analysis_method": "Error occurred"
            },
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
