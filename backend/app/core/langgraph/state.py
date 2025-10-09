from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class ResearchContext(TypedDict):
    product_idea: str
    sector: str
    research_depth: str
    max_sources: int
    request_id: str
    created_at: str
    updated_at: str

class AgentResult(TypedDict):
    agent_name: str
    status: str
    analysis: Optional[Dict[str, Any]]
    sources_analyzed: int
    data_sources: Dict[str, Any]
    error: Optional[str]
    timestamp: str

class ResearchState(TypedDict):
    context: ResearchContext
    market_result: Optional[AgentResult]
    competitor_result: Optional[AgentResult] 
    customer_result: Optional[AgentResult]
    report_result: Optional[AgentResult]
    current_step: str
    progress: int
    status: str
    messages: Annotated[List[BaseMessage], add_messages]
    research_plan: Optional[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    errors: List[str]
    abort_requested: bool
    stream_data: Dict[str, Any]

def create_initial_state(
    product_idea: str,
    sector: str,
    research_depth: str = "standard",
    request_id: str = "unknown"
) -> ResearchState:
    now = datetime.now().isoformat()
    
    return ResearchState(
        context=ResearchContext(
            product_idea=product_idea,
            sector=sector,
            research_depth=research_depth,
            max_sources=20,  # Hard-coded to 20 for all tasks
            request_id=request_id,
            created_at=now,
            updated_at=now
        ),
        market_result=None,
        competitor_result=None,
        customer_result=None,
        report_result=None,
        current_step="initializing",
        progress=0,
        status="initializing",
        messages=[],
        research_plan=None,
        final_report=None,
        errors=[],
        abort_requested=False,
        stream_data={}
    )

def add_error_to_state(state: ResearchState, error: str) -> ResearchState:
    state["errors"].append(f"{datetime.now().isoformat()}: {error}")
    state["status"] = "failed"
    return state

def mark_aborted(state: ResearchState) -> ResearchState:
    state["status"] = "aborted"
    state["abort_requested"] = True
    state["updated_at"] = datetime.now().isoformat()
    return state

def mark_completed(state: ResearchState) -> ResearchState:
    state["status"] = "completed"
    state["progress"] = 100
    state["updated_at"] = datetime.now().isoformat()
    return state
