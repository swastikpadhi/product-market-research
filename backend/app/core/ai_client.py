"""
Simplified AI Client - Direct LLM access
"""
from langchain_openai import ChatOpenAI
from app.core.config import settings

# Singleton instance for mock LLM to maintain call counter
_mock_llm_instance = None

def get_llm_client(api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.1):
    """Get LLM client (real or mock based on environment)"""
    # Use mocks if environment=development
    if settings.environment.lower() == 'development':
        global _mock_llm_instance
        if _mock_llm_instance is None:
            from app.mocks.mock_llm import MockChatOpenAI
            _mock_llm_instance = MockChatOpenAI(model=model, api_key=api_key, temperature=temperature)
        return _mock_llm_instance
    
    # Use real LLM
    return ChatOpenAI(model=model, api_key=api_key, temperature=temperature)
