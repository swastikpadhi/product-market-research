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
        # Use consistent AI client pattern
        from app.core.ai_client import get_llm_client
        self.llm = get_llm_client(openai_api_key)
        
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
            
            # Create research plan if not already created
            if state.get("research_plan") is None:
                research_plan = await self._parse_and_generate_queries(
                    context["product_idea"], request_id
                )
                state["research_plan"] = research_plan
                progress_tracker.complete_checkpoint(request_id, "research_plan_created")
            
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
        
        # Fail fast on any errors - don't continue the workflow
        if state.get("errors") and len(state["errors"]) > 0:
            logger.error(f"Workflow has errors, failing: {state['errors']}")
            return "finalization"
        
        # Check if we have research plan
        if state.get("research_plan") is None:
            return "parallel_analysis"
        
        # Check if parallel analysis is complete
        if (state["market_result"] is None and
                state["competitor_result"] is None and
                state["customer_result"] is None):
            return "parallel_analysis"
        
        # Check if report generation is needed
        if state["report_result"] is None:
            return "report_generation"
            
        return "finalization"
    
    def _supervisor_router(self, state: ResearchState) -> str:
        return state["current_step"]
    
    
    async def _parallel_analysis_node(self, state: ResearchState) -> ResearchState:
        try:
            context = state["context"]
            request_id = context["request_id"]

            # Get queries from research plan
            research_plan = state.get("research_plan", {})
            if not research_plan:
                return add_error_to_state(state, "Research plan not found")
            
            # Extract queries from research plan using original format
            queries = {
                'market': research_plan.get('market_query', ''),
                'competitor': research_plan.get('competitor_query', ''),
                'customer': research_plan.get('customer_query', '')
            }
            
            # Debug logging to check query values
            logger.info(f"[{request_id}] Extracted queries: market='{queries['market']}', competitor='{queries['competitor']}', customer='{queries['customer']}'")
            
            # Checkpoint 2: Queries generated (search queries ready)
            progress_tracker.complete_checkpoint(request_id, "queries_generated")
            
            import asyncio
            tasks = [
                self.market_agent.analyze_market_trends(
                    query=queries['market'],
                    context=context,
                    request_id=request_id
                ),
                self.competitor_agent.analyze_competitors(
                    query=queries['competitor'],
                    context=context,
                    request_id=request_id
                ),
                self.customer_agent.analyze_customer_insights(
                    query=queries['customer'],
                    context=context,
                    request_id=request_id
                )
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Fail fast on any agent failures
            if isinstance(results[0], Exception):
                error_msg = f"Market agent failed: {results[0]}"
                logger.error(f"[{request_id}] {error_msg}")
                return add_error_to_state(state, error_msg)
            if isinstance(results[1], Exception):
                error_msg = f"Competitor agent failed: {results[1]}"
                logger.error(f"[{request_id}] {error_msg}")
                return add_error_to_state(state, error_msg)
            if isinstance(results[2], Exception):
                error_msg = f"Customer agent failed: {results[2]}"
                logger.error(f"[{request_id}] {error_msg}")
                return add_error_to_state(state, error_msg)
            
            # Check if any agent returned an error status
            market_result = results[0]
            competitor_result = results[1]
            customer_result = results[2]
            
            if market_result and market_result.get("status") == "error":
                error_msg = f"Market analysis failed: {market_result.get('error', 'Unknown error')}"
                logger.error(f"[{request_id}] {error_msg}")
                return add_error_to_state(state, error_msg)
            if competitor_result and competitor_result.get("status") == "error":
                error_msg = f"Competitor analysis failed: {competitor_result.get('error', 'Unknown error')}"
                logger.error(f"[{request_id}] {error_msg}")
                return add_error_to_state(state, error_msg)
            if customer_result and customer_result.get("status") == "error":
                error_msg = f"Customer analysis failed: {customer_result.get('error', 'Unknown error')}"
                logger.error(f"[{request_id}] {error_msg}")
                return add_error_to_state(state, error_msg)
            
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

            # Check if all 3 analysis agents were successful before generating report
            market_success = state.get("market_result", {}).get("status") == "success"
            competitor_success = state.get("competitor_result", {}).get("status") == "success"
            customer_success = state.get("customer_result", {}).get("status") == "success"
            
            if not (market_success and competitor_success and customer_success):
                failed_agents = []
                if not market_success:
                    failed_agents.append("market analysis")
                if not competitor_success:
                    failed_agents.append("competitor analysis")
                if not customer_success:
                    failed_agents.append("customer analysis")
                
                error_msg = f"Cannot generate report: {', '.join(failed_agents)} failed"
                logger.error(f"[{request_id}] {error_msg}")
                return add_error_to_state(state, error_msg)

            progress_tracker.complete_checkpoint(request_id, "report_generation_started")
            
            result = await self.report_agent.generate_report(
                market_result=state["market_result"],
                competitor_result=state["competitor_result"],
                customer_result=state["customer_result"],
                context=context,
                request_id=request_id
            )
            
            # Fail fast if report generation failed
            if result and result.get("status") == "error":
                error_msg = f"Report generation failed: {result.get('error', 'Unknown error')}"
                logger.error(f"[{request_id}] {error_msg}")
                return add_error_to_state(state, error_msg)
            
            state["report_result"] = result
            state["final_report"] = result.get("final_report", {})
            
            progress_tracker.complete_checkpoint(request_id, "report_generation_completed")
            
            return state
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return add_error_to_state(state, f"Report generation error: {str(e)}")
    
    async def _finalization_node(self, state: ResearchState) -> ResearchState:
        try:
            context = state["context"]
            request_id = context["request_id"]

            progress_tracker.complete_checkpoint(request_id, "final_report_delivered")
            
            state = mark_completed(state)
            
            return state
            
        except Exception as e:
            logger.error(f"Finalization error: {e}")
            return add_error_to_state(state, f"Finalization error: {str(e)}")
    
    async def _parse_and_generate_queries(self, product_idea: str, request_id: str) -> Dict[str, Any]:
        # Checkpoint: Queries generated (moved to parallel_analysis_node)
        
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
    
    def execute_research_sync(
        self,
        product_idea: str,
        sector: str,
        research_depth: str = "standard",
        request_id: str = "unknown",
        abort_check: Optional[Callable[[], bool]] = None,
        progress_callback: Optional[Callable[[str, int, str], Any]] = None
    ) -> Dict[str, Any]:
        """Sync version of execute_research for Celery workers"""
        import asyncio
        
        # Create a new event loop for this sync method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.execute_research(
                product_idea=product_idea,
                sector=sector,
                research_depth=research_depth,
                request_id=request_id,
                abort_check=abort_check,
                progress_callback=progress_callback
            ))
        finally:
            loop.close()
