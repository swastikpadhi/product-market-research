import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.utils import extract_json_from_response
from app.core.prompts import format_report_generator_prompt
from app.core.config import get_logger

logger = get_logger(__name__)

class ReportGenerationAgent:

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key, temperature=0.1)
    
    async def generate_report(
        self,
        market_result: Optional[Dict[str, Any]],
        competitor_result: Optional[Dict[str, Any]],
        customer_result: Optional[Dict[str, Any]],
        context: Dict[str, Any],
        request_id: str = "unknown"
    ) -> Dict[str, Any]:
        
        try:
            product_idea = context.get("product_idea", "")
            sector = context.get("sector", "")
            
            market_analysis = market_result.get("analysis", {}) if market_result.get("status") == "success" else {}
            competitor_analysis = (competitor_result.get("analysis", {})
                                   if competitor_result.get("status") == "success" else {})
            customer_insights = (customer_result.get("analysis", {})
                                 if customer_result.get("status") == "success" else {})
            
            market_count = market_result.get("sources_analyzed", 0) if market_result else 0
            competitor_count = competitor_result.get("sources_analyzed", 0) if competitor_result else 0
            customer_count = customer_result.get("sources_analyzed", 0) if customer_result else 0
            
            system_prompt, human_prompt = format_report_generator_prompt(
                sector=sector,
                product_idea=product_idea,
                market_analysis=json.dumps(market_analysis, indent=2),
                competitor_analysis=json.dumps(competitor_analysis, indent=2),
                customer_insights=json.dumps(customer_insights, indent=2),
                market_count=market_count,
                competitor_count=competitor_count,
                customer_count=customer_count
            )
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ])
            
            json_content = extract_json_from_response(response.content)
            final_report = json.loads(json_content)
            
            result = {
                "agent_name": "ReportGenerationAgent",
                "status": "success",
                "final_report": final_report,
                "sources_analyzed": market_count + competitor_count + customer_count,
                "data_sources": {
                    "market_sources": market_count,
                    "competitor_sources": competitor_count,
                    "customer_sources": customer_count,
                    "total_sources": market_count + competitor_count + customer_count,
                    "analysis_method": "LangGraph-enhanced report generation"
                },
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "sector": sector,
                    "product_idea": product_idea,
                    "research_depth": context.get("research_depth", "standard")
                }
            }
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"[{request_id}] ReportGenerationAgent: JSON parsing failed - {e}")
            return self._create_error_result(context, f"JSON parsing error: {str(e)}")
            
        except Exception as e:
            logger.error(f"[{request_id}] ReportGenerationAgent: Report generation failed - {e}")
            return self._create_error_result(context, str(e))
    
    def _create_error_report(self, error_msg: str) -> Dict[str, Any]:
        return {
            "market_insights": {
                "market_size": "See raw analysis", 
                "growth_rate": "Error", 
                "key_trends": [], 
                "market_drivers": [], 
                "future_outlook": ""
            },
            "competitive_landscape": {
                "competitive_landscape": "", 
                "market_leaders": [], 
                "key_competitors": [], 
                "competitive_gaps": [], 
                "pricing_landscape": ""
            },
            "customer_insights": {
                "primary_pain_points": [], 
                "unmet_needs": [], 
                "customer_segments": [], 
                "satisfaction_drivers": [], 
                "feature_priorities": []
            },
            "pmf_assessment": {
                "market_opportunities": [], 
                "product_fit_score": "Error", 
                "key_risks": [], 
                "success_probability": "Unknown", 
                "time_to_market": "Error"
            },
            "strategic_recommendations": {
                "immediate_actions": [], 
                "product_development": [], 
                "market_entry": [], 
                "competitive_strategy": [], 
                "success_metrics": []
            },
            "synthesis": {
                "executive_summary": f"Report generation failed: {error_msg}",
                "key_insights": [{
                    "insight": "Error occurred during report generation", 
                    "impact": "High", 
                    "confidence": "Low"
                }],
                "actionable_recommendations": ["Please retry the research task"],
                "next_steps": ["Contact support if the issue persists"]
            }
        }
    
    def _create_error_result(self, context: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        return {
            "agent_name": "ReportGenerationAgent",
            "status": "error",
            "error": error_msg,
            "final_report": self._create_error_report(error_msg),
            "sources_analyzed": 0,
            "data_sources": {
                "market_sources": 0,
                "competitor_sources": 0,
                "customer_sources": 0,
                "total_sources": 0,
                "analysis_method": "Error occurred"
            },
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
