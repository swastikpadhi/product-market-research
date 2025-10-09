import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SimpleTavilyClient:
    def __init__(self, request_id: str, api_key: str = None):
        self.request_id = request_id
        self.api_key = api_key or self._get_api_key()
    
    def _get_api_key(self) -> str:
        """Get Tavily API key from environment"""
        from app.core.config import settings
        return settings.tavily_api_key
    
    def search(self, query: str, search_depth: str = "basic", max_results: int = 10, 
               include_answer: bool = True, include_raw_content: bool = False) -> Dict[str, Any]:
        
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
            
            logger.info(f"[{self.request_id}] Making real Tavily API call with query: '{query}'")
            logger.info(f"[{self.request_id}] Tavily API payload: {payload}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"[{self.request_id}] Tavily API returned {len(result.get('results', []))} results")
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Tavily API call failed: {e}")
            raise Exception(f"Tavily search API failed: {str(e)}")
    
    def extract(self, urls: List[str], extract_depth: str = "basic") -> Dict[str, Any]:
        
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
            
            logger.info(f"[{self.request_id}] Making real Tavily extract API call for {len(urls)} URLs with timeout=60s")
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"[{self.request_id}] Tavily extract API returned {len(result.get('results', []))} results")
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.request_id}] Tavily extract API call failed: {e}")
            raise Exception(f"Tavily extract API failed: {str(e)}")
