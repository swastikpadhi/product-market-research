"""
Mock LLM for testing without spending OpenAI credits
Uses comprehensive mock responses for all 17 checkpoints
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class MockChatOpenAI:
    """Mock ChatOpenAI that returns realistic responses using comprehensive mock data"""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: str = "mock_key", temperature: float = 0.1):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.call_count = 0
        self.total_tokens_used = 0
        
        # Import comprehensive mock responses
        from app.mocks.comprehensive_mock_responses import comprehensive_mock_responses
        self.mock_responses = comprehensive_mock_responses
        
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Mock invoke method that returns realistic responses"""
        return self._process_messages(messages, **kwargs)
    
    async def ainvoke(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Mock async invoke method that returns realistic responses"""
        return self._process_messages(messages, **kwargs)
    
    def _process_messages(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process messages and return mock response based on comprehensive mock data"""
        self.call_count += 1
        
        # Log OpenAI call clearly with consistent format
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[MOCK] Using MOCK OpenAI API (call #{self.call_count})")
        
        # Extract the last user message with better debugging
        user_message = ""
        for msg in reversed(messages):
            if isinstance(msg, dict):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            elif hasattr(msg, 'content'):
                user_message = getattr(msg, 'content', "")
                break
        
        # Debug logging for message extraction
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[MOCK] Extracted user message: '{user_message[:100]}...' (length: {len(user_message)})")
        
        # Generate response based on message content and context
        response_content = self._generate_contextual_response(user_message)
        
        # Calculate token usage (rough estimate)
        input_tokens = sum(len(str(msg).split()) for msg in messages)
        output_tokens = len(response_content.split())
        total_tokens = input_tokens + output_tokens
        self.total_tokens_used += total_tokens
        
        # Create mock response object
        class MockResponse:
            def __init__(self, content: str, model: str):
                self.content = content
                self.model = model  # Add model attribute
                self.response_metadata = {
                    "model": model,
                    "usage": {
                        "prompt_tokens": input_tokens,
                        "completion_tokens": output_tokens,
                        "total_tokens": total_tokens
                    }
                }
        
        return MockResponse(response_content, self.model)
    
    def _generate_contextual_response(self, user_message: str) -> str:
        """Generate contextual response based on message content"""
        user_message_lower = user_message.lower()
        
        # Debug logging with consistent format
        import logging
        logger = logging.getLogger(__name__)
        detected_keywords = [k for k in ['report', 'summary', 'final', 'conclusion', 'comprehensive', 'product-market fit'] if k in user_message_lower]
        logger.info(f"[MOCK] Processing message with keywords: {detected_keywords}")
        
        # Research plan and initialization
        if any(keyword in user_message_lower for keyword in ["research plan", "initialization", "workflow", "product idea", "generate 3 search queries", "validate this input"]):
            plan_data = self.mock_responses.get_mock_research_plan()
            return json.dumps(plan_data, indent=2)
        
        # Market analysis
        elif any(keyword in user_message_lower for keyword in ["market", "industry", "size", "growth"]):
            if "search" in user_message_lower:
                search_data = self.mock_responses.get_mock_market_search_results()
                return json.dumps(search_data, indent=2)
            elif "extraction" in user_message_lower:
                extraction_data = self.mock_responses.get_mock_market_extraction_results()
                return json.dumps(extraction_data, indent=2)
            else:
                analysis_data = self.mock_responses.get_mock_market_analysis()
                return json.dumps(analysis_data, indent=2)
        
        # Competitor analysis
        elif any(keyword in user_message_lower for keyword in ["competitor", "competition", "rival"]):
            if "search" in user_message_lower:
                search_data = self.mock_responses.get_mock_competitor_search_results()
                return json.dumps(search_data, indent=2)
            elif "extraction" in user_message_lower:
                extraction_data = self.mock_responses.get_mock_competitor_extraction_results()
                return json.dumps(extraction_data, indent=2)
            else:
                analysis_data = self.mock_responses.get_mock_competitor_analysis()
                return json.dumps(analysis_data, indent=2)
        
        # Customer analysis
        elif any(keyword in user_message_lower for keyword in ["customer", "user", "persona", "behavior"]):
            if "search" in user_message_lower:
                search_data = self.mock_responses.get_mock_customer_search_results()
                return json.dumps(search_data, indent=2)
            elif "extraction" in user_message_lower:
                extraction_data = self.mock_responses.get_mock_customer_extraction_results()
                return json.dumps(extraction_data, indent=2)
            else:
                analysis_data = self.mock_responses.get_mock_customer_analysis()
                return json.dumps(analysis_data, indent=2)
        
        # Report generation
        elif any(keyword in user_message_lower for keyword in ["report", "summary", "final", "conclusion", "comprehensive", "product-market fit"]):
            if "generation" in user_message_lower:
                logger.info(f"[MOCK] Returning report generation data")
                report_data = self.mock_responses.get_mock_report_generation_data()
                return json.dumps(report_data, indent=2)
            else:
                logger.info(f"[MOCK] Returning final report data")
                final_report = self.mock_responses.get_mock_final_report()
                logger.info(f"[MOCK] Final report has mock marker: {'mock' in final_report}")
                return json.dumps(final_report, indent=2)
        
        # Search queries generation
        elif any(keyword in user_message_lower for keyword in ["query", "search", "keywords"]):
            queries_data = self.mock_responses.get_mock_queries()
            return json.dumps(queries_data, indent=2)
        
        # Default response for other cases
        else:
            return json.dumps({
                "response": "Mock AI response for testing",
                "message": user_message,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "call_count": self.call_count
            }, indent=2)

# Global instance for easy access
mock_llm = MockChatOpenAI()