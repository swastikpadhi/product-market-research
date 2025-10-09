import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import ResearchState, create_initial_state, add_error_to_state, mark_completed, mark_aborted
from .agents import (
    MarketAnalysisAgent,
    CompetitorAnalysisAgent,
    CustomerInsightsAgent,
    ReportGenerationAgent
)
from app.core.config import get_logger
from app.core.utils import extract_json_from_response
from app.core.prompts import format_orchestrator_parse_prompt
from app.services.progress_tracker import progress_tracker

logger = get_logger(__name__)

class ResearchSupervisor:

    def __init__(self, openai_api_key: str, tavily_api_key: str):
        self.openai_api_key = openai_api_key
        self.tavily_api_key = tavily_api_key
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key, temperature=0.1)
        
        self.market_agent = MarketAnalysisAgent(openai_api_key, tavily_api_key)
        self.competitor_agent = CompetitorAnalysisAgent(openai_api_key, tavily_api_key)
        self.customer_agent = CustomerInsightsAgent(openai_api_key, tavily_api_key)
        self.report_agent = ReportGenerationAgent(openai_api_key)
        
        self.workflow = self._create_workflow()
        
    def _create_workflow(self) -> StateGraph:
        workflow = StateGraph(ResearchState)
        
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("parallel_analysis", self._parallel_analysis_node)
        workflow.add_node("report_generation", self._report_generation_node)
        workflow.add_node("finalization", self._finalization_node)
        
        workflow.add_edge(START, "supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            self._supervisor_router,
            {
                "parallel_analysis": "parallel_analysis",
                "report_generation": "report_generation",
                "finalization": "finalization",
                "end": END
            }
        )
        
        workflow.add_edge("parallel_analysis", "report_generation")
        
        workflow.add_edge("report_generation", "finalization")
        workflow.add_edge("finalization", END)
        
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    async def _supervisor_node(self, state: ResearchState) -> ResearchState:
        try:
            context = state["context"]
            request_id = context["request_id"]

            if state.get("abort_requested", False):
                return mark_aborted(state)
            
            next_step = await self._determine_next_step(state)
            state["current_step"] = next_step
            
            state["messages"].append(
                AIMessage(content=f"Supervisor decided: {next_step}")
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Supervisor node error: {e}")
            return add_error_to_state(state, f"Supervisor error: {str(e)}")
    
    async def _determine_next_step(self, state: ResearchState) -> str:
        context = state["context"]
        
        if state.get("errors") and len(state["errors"]) > 0:
            return "finalization"
        
        if (state["market_result"] is None and
                state["competitor_result"] is None and
                state["customer_result"] is None):
            return "parallel_analysis"
        
        if state["report_result"] is None:
            return "report_generation"
            
        return "finalization"
    
    def _supervisor_router(self, state: ResearchState) -> str:
        return state["current_step"]
    
    def _analysis_router(self, state: ResearchState) -> str:
        if (state["market_result"] and state["competitor_result"] and
                state["customer_result"] and state["report_result"] is None):
            return "report_generation"
        
        return "next_analysis"
    
    async def _parallel_analysis_node(self, state: ResearchState) -> ResearchState:
        try:
            context = state["context"]
            request_id = context["request_id"]

            from app.services.progress_tracker import progress_tracker
            await progress_tracker.complete_checkpoint(request_id, "initialization_complete")
            
            if not hasattr(self, '_queries'):
                parsed_input = await self._parse_and_generate_queries(
                    context["product_idea"], request_id
                )
                self._queries = {
                    'market': parsed_input['market_query'],
                    'competitor': parsed_input['competitor_query'],
                    'customer': parsed_input['customer_query']
                }
                self._sector = parsed_input['sector']
            
            import asyncio
            tasks = [
                self.market_agent.analyze_market_trends(
                    query=self._queries['market'],
                    context=context,
                    request_id=request_id
                ),
                self.competitor_agent.analyze_competitors(
                    query=self._queries['competitor'],
                    context=context,
                    request_id=request_id
                ),
                self.customer_agent.analyze_customer_insights(
                    query=self._queries['customer'],
                    context=context,
                    request_id=request_id
                )
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            market_result = results[0] if not isinstance(results[0], Exception) else None
            competitor_result = results[1] if not isinstance(results[1], Exception) else None
            customer_result = results[2] if not isinstance(results[2], Exception) else None
            
            state["market_result"] = market_result
            state["competitor_result"] = competitor_result
            state["customer_result"] = customer_result
            
            return state
            
        except Exception as e:
            logger.error(f"Parallel analysis error: {e}")
            return add_error_to_state(state, f"Parallel analysis error: {str(e)}")

    async def _report_generation_node(self, state: ResearchState) -> ResearchState:
        try:
            context = state["context"]
            request_id = context["request_id"]

            from app.services.progress_tracker import progress_tracker
            await progress_tracker.complete_checkpoint(request_id, "report_generation_started")
            
            result = await self.report_agent.generate_report(
                market_result=state["market_result"],
                competitor_result=state["competitor_result"],
                customer_result=state["customer_result"],
                context=context,
                request_id=request_id
            )
            
            state["report_result"] = result
            state["final_report"] = result.get("final_report", {})
            
            await progress_tracker.complete_checkpoint(request_id, "report_generation_completed")
            
            return state
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return add_error_to_state(state, f"Report generation error: {str(e)}")
    
    async def _finalization_node(self, state: ResearchState) -> ResearchState:
        try:
            context = state["context"]
            request_id = context["request_id"]

            from app.services.progress_tracker import progress_tracker
            await progress_tracker.complete_checkpoint(request_id, "finalization_complete")
            
            state = mark_completed(state)
            
            return state
            
        except Exception as e:
            logger.error(f"Finalization error: {e}")
            return add_error_to_state(state, f"Finalization error: {str(e)}")
    
    async def _parse_and_generate_queries(self, product_idea: str, request_id: str) -> Dict[str, Any]:
        # Checkpoint: Queries generated
        await progress_tracker.complete_checkpoint(request_id, "queries_generated")
        
        system_prompt, human_prompt = format_orchestrator_parse_prompt(product_idea)
        
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])
        
        json_content = extract_json_from_response(response.content)
        parsed = json.loads(json_content)
        
        return parsed
    
    async def execute_research(
        self,
        product_idea: str,
        sector: str,
        research_depth: str = "standard",
        request_id: str = "unknown",
        abort_check: Optional[Callable[[], bool]] = None,
        progress_callback: Optional[Callable[[str, int, str], Any]] = None
    ) -> Dict[str, Any]:
        
        try:
            initial_state = create_initial_state(
                product_idea=product_idea,
                sector=sector,
                research_depth=research_depth,
                request_id=request_id
            )
            
            config = {
                "configurable": {"thread_id": request_id},
                "recursion_limit": 50
            }
            final_state = None
            async for chunk in self.workflow.astream(initial_state, config=config):
                if progress_callback:
                    await self._handle_streaming_update(chunk, progress_callback)
                
                if abort_check and abort_check():
                    break
                
                final_state = chunk
            
            if not final_state:
                return {
                    "success": False,
                    "error": "Workflow execution failed",
                    "request_id": request_id
                }
            
            if final_state:
                state = final_state.get(list(final_state.keys())[0])
                if state:
                    if state.get("status") == "completed":
                        return self._build_success_response(state)
                    else:
                        return self._build_error_response(state)
            
            return {
                "success": False,
                "error": "No final state found",
                "request_id": request_id
            }
                
        except Exception as e:
            logger.error(f"Research execution failed: {e}")
            return {
                "success": False,
                "error": f"Research execution failed: {str(e)}",
                "request_id": request_id
            }
    
    async def _handle_streaming_update(self, chunk: Dict, progress_callback: Callable):
        try:
            for node_name, state in chunk.items():
                if isinstance(state, dict) and "progress" in state:
                    await progress_callback(
                        state.get("current_step", "processing"),
                        state.get("progress", 0),
                        f"Node: {node_name}"
                    )
        except Exception as e:
            logger.warning(f"Streaming update error: {e}")
    
    def _build_success_response(self, state: ResearchState) -> Dict[str, Any]:
        return {
            "success": True,
            "research_plan": state.get("research_plan", {}),
            "market_trends_result": state.get("market_result", {}),
            "competitor_result": state.get("competitor_result", {}),
            "customer_result": state.get("customer_result", {}),
            "synthesis_result": state.get("report_result", {}),
            "final_report": state.get("final_report", {}),
            "metadata": {
                "sector": state["context"]["sector"],
                "max_sources": state["context"]["max_sources"],
                "research_depth": state["context"]["research_depth"],
                "request_id": state["context"]["request_id"],
                "completed_at": state["context"]["updated_at"]
            }
        }
    
    def _build_error_response(self, state: ResearchState) -> Dict[str, Any]:
        return {
            "success": False,
            "error": f"Research failed: {state.get('status', 'unknown')}",
            "errors": state.get("errors", []),
            "partial_results": {
                "market": state.get("market_result"),
                "competitor": state.get("competitor_result"),
                "customer": state.get("customer_result"),
                "report": state.get("report_result")
            },
            "request_id": state["context"]["request_id"]
        }
