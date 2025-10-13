import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SimpleTavilyClient:
    def __init__(self, request_id: str, api_key: str = None):
        self.request_id = request_id
        self.api_key = api_key or self._get_api_key()
        self._mock_client = None
        self._should_use_mock = self._check_mock_mode()
    
    def _get_api_key(self) -> str:
        """Get Tavily API key from environment"""
        from app.core.config import settings
        return settings.tavily_api_key
    
    def _check_mock_mode(self) -> bool:
        """Check if mocks should be used based on environment"""
        from app.core.config import settings
        
        # Use mocks if environment=development
        return settings.environment.lower() == 'development'
    
    def _get_mock_client(self):
        """Get mock Tavily client"""
        if self._mock_client is None:
            from app.mocks.tavily_mock import MockTavilyClient
            self._mock_client = MockTavilyClient(api_key="mock_key")
        return self._mock_client
    
    def search(self, query: str, search_depth: str = "basic", max_results: int = 10, 
               include_answer: bool = True, include_raw_content: bool = False) -> Dict[str, Any]:
        
        # Use mock if enabled
        if self._should_use_mock:
            logger.info(f"[{self.request_id}] Using MOCK Tavily Search API for query: '{query}'")
            mock_client = self._get_mock_client()
            result = mock_client.search(query, search_depth, max_results)
            logger.info(f"[{self.request_id}] Mock Tavily Search API returned {len(result.get('results', []))} results")
            return result
        
        # Use real API
        try:
            import requests
            
            url = "https://api.tavily.com/search"
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": search_depth,
                "max_results": 20
            }
            
            logger.info(f"[{self.request_id}] Making real Tavily Search API call with query: '{query}'")
            logger.info(f"[{self.request_id}] Tavily Search API payload: {payload}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"[{self.request_id}] Tavily Search API returned {len(result.get('results', []))} results")
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Tavily API call failed: {e}")
            raise Exception(f"Tavily search API failed: {str(e)}")
    
    def extract(self, urls: List[str], extract_depth: str = "basic") -> Dict[str, Any]:
        
        # Use mock if enabled
        if self._should_use_mock:
            logger.info(f"[{self.request_id}] Using MOCK Tavily Extract API for {len(urls)} URLs")
            mock_client = self._get_mock_client()
            # Generate mock extract results
            mock_results = []
            for i, url in enumerate(urls):
                mock_results.append({
                    "url": url,
                    "content": f"Mock extracted content from {url}. This is simulated content for testing purposes. Content includes relevant information about the topic with detailed analysis and insights.",
                    "title": f"Mock Article {i+1}",
                    "score": 0.8 + (i * 0.05)
                })
            
            result = {"results": mock_results}
            logger.info(f"[{self.request_id}] Mock Tavily Extract API returned {len(result.get('results', []))} results")
            return result
        
        # Use real API
        try:
            import requests
            
            url = "https://api.tavily.com/extract"
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "api_key": self.api_key,
                "urls": urls,
                "extract_depth": extract_depth,
                "timeout": 60
            }
            
            logger.info(f"[{self.request_id}] Making real Tavily Extract API call for {len(urls)} URLs with timeout=60s")
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"[{self.request_id}] Tavily Extract API returned {len(result.get('results', []))} results")
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Tavily extract API call failed: {e}")
            raise Exception(f"Tavily extract API failed: {str(e)}")
