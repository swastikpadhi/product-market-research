"""
Constants used across the application
"""

# All checkpoints in the research workflow
ALL_CHECKPOINTS = [
    "research_plan_created",
    "queries_generated", 
    "market_search_started",
    "market_search_completed",
    "market_extraction_completed",
    "market_analysis_completed",
    "competitor_search_started",
    "competitor_search_completed", 
    "competitor_extraction_completed",
    "competitor_analysis_completed",
    "customer_search_started",
    "customer_search_completed",
    "customer_extraction_completed", 
    "customer_analysis_completed",
    "report_generation_started",
    "report_generation_completed",
    "final_report_delivered"
]

TOTAL_CHECKPOINTS = len(ALL_CHECKPOINTS)

# OpenAI API limits
MAX_CHARACTERS_PER_REQUEST = 320000  # Conservative estimate: 1 token ≈ 3.5 characters, 96k * 3.5 = 336k, use 320k for safety
