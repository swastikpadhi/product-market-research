"""
Research Schemas - Pydantic models for API validation
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ResearchRequest(BaseModel):
    product_idea: str
    research_depth: str = "standard"

class ResearchResponse(BaseModel):
    request_id: str
    status: str
    message: str

class ResearchStatus(BaseModel):
    request_id: str
    status: str
    current_step: str
    progress: int
    details: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    research_depth: str
    product_idea: str
    completed_checkpoints: list = []
    total_checkpoints: int = 17
    last_updated: Optional[str] = None

class ResearchResult(BaseModel):
    request_id: str
    status: str
    result: Dict[str, Any]
    metadata: Dict[str, Any]

class SearchesRemaining(BaseModel):
    searches_remaining: Dict[str, int]
    credit_balance: float
    user_id: str

class TaskList(BaseModel):
    research_tasks: list
    page: int
    page_size: int
    total: int
    total_pages: int

class TaskReport(BaseModel):
    request_id: str
    status: str
    final_report: Dict[str, Any]

class TaskAction(BaseModel):
    message: str

class CreditAddition(BaseModel):
    success: bool
    message: str
    balance_after: float
