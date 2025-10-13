"""
Mock Tavily API for testing without spending credits
Uses comprehensive mock responses for all search and extraction operations
"""
import json
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

class MockTavilyClient:
    """Mock Tavily client that returns realistic search results using comprehensive mock data"""
    
    def __init__(self, api_key: str = "mock_key"):
        self.api_key = api_key
        self.call_count = 0
        
        # Import comprehensive mock responses
        from app.mocks.comprehensive_mock_responses import comprehensive_mock_responses
        self.mock_responses = comprehensive_mock_responses
        
    def search(self, query: str, search_depth: str = "basic", max_results: int = 5) -> Dict[str, Any]:
        """Mock search method that returns realistic results using comprehensive mock data"""
        self.call_count += 1
        
        # Determine search type based on query content
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ["market", "industry", "size", "growth", "trends"]):
            # Market search
            search_data = self.mock_responses.get_mock_market_search_results()
            return search_data
        elif any(keyword in query_lower for keyword in ["competitor", "competition", "rival", "vs", "comparison"]):
            # Competitor search
            search_data = self.mock_responses.get_mock_competitor_search_results()
            return search_data
        elif any(keyword in query_lower for keyword in ["customer", "user", "persona", "behavior", "needs"]):
            # Customer search
            search_data = self.mock_responses.get_mock_customer_search_results()
            return search_data
        else:
            # Default search results
            return self._generate_default_search_results(query, search_depth, max_results)
    
    def extract(self, urls: List[str], extract_depth: str = "basic") -> Dict[str, Any]:
        """Mock extract method that returns realistic content using comprehensive mock data"""
        self.call_count += 1
        
        # Determine extraction type based on URL content or context
        # For now, return market extraction as default since it's most comprehensive
        extraction_data = self.mock_responses.get_mock_market_extraction_results()
        return extraction_data
    
    def _generate_default_search_results(self, query: str, search_depth: str, max_results: int) -> Dict[str, Any]:
        """Generate default search results when query doesn't match specific patterns"""
        return {
            "query": query,
            "follow_up_questions": [
                f"What are the key trends in {query}?",
                f"How is {query} evolving?",
                f"What are the main challenges in {query}?"
            ],
            "answer": f"Comprehensive analysis of {query} reveals significant opportunities and challenges in the current market landscape.",
            "images": [],
            "results": [
                {
                    "title": f"Analysis of {query} - Market Report 2024",
                    "url": f"https://example.com/{query.replace(' ', '-').lower()}-report",
                    "content": f"Detailed analysis of {query} including market trends, opportunities, and strategic recommendations.",
                    "score": 0.85,
                    "published_date": "2024-01-15"
                }
            ],
            "response_time": random.uniform(0.5, 2.0)
        }
    
    def _generate_mock_results(self, query: str, search_depth: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate realistic mock search results"""
        results = []
        
        # Base domains for different types of queries
        domains = [
            "techcrunch.com", "forbes.com", "reuters.com", "bloomberg.com",
            "wsj.com", "nytimes.com", "cnn.com", "bbc.com", "theguardian.com",
            "venturebeat.com", "mashable.com", "wired.com", "arstechnica.com"
        ]
        
        # Generate results based on query keywords
        query_lower = query.lower()
        
        for i in range(min(max_results, 5)):
            # Generate realistic content based on query
            title = self._generate_title(query)
            content = self._generate_content(query, search_depth)
            
            result = {
                "title": title,
                "url": f"https://{random.choice(domains)}/article/{i+1}",
                "content": content,
                "score": round(random.uniform(0.7, 0.95), 2),
                "published_date": self._generate_published_date()
            }
            results.append(result)
        
        return results
    
    def _generate_title(self, query: str) -> str:
        """Generate realistic article titles"""
        query_lower = query.lower()
        
        if "ai" in query_lower or "artificial intelligence" in query_lower:
            titles = [
                f"AI Revolution: How {query} is Transforming Industries",
                f"The Future of {query}: AI-Powered Solutions",
                f"Breaking: {query} Gets Major AI Investment",
                f"AI Startup {query} Raises $50M in Series A"
            ]
        elif "startup" in query_lower or "company" in query_lower:
            titles = [
                f"{query} Secures $10M Funding Round",
                f"Startup {query} Disrupts Traditional Market",
                f"{query} Expands to European Markets",
                f"Tech Company {query} Reports Record Growth"
            ]
        elif "market" in query_lower or "research" in query_lower:
            titles = [
                f"Market Analysis: {query} Shows Strong Growth",
                f"Research Report: {query} Market Trends 2024",
                f"Industry Insights: {query} Market Opportunities",
                f"Market Research: {query} Consumer Behavior"
            ]
        else:
            titles = [
                f"Latest Updates on {query}",
                f"{query}: Industry Analysis and Trends",
                f"Breaking News: {query} Development",
                f"Expert Analysis: {query} Market Impact"
            ]
        
        return random.choice(titles)
    
    def _generate_content(self, query: str, search_depth: str) -> str:
        """Generate realistic article content"""
        base_content = f"""
        {query} represents a significant opportunity in today's market. 
        Recent developments show strong growth potential with increasing 
        consumer demand and technological advancements.
        """
        
        if search_depth == "advanced":
            base_content += f"""
            
            Market Analysis:
            - Market size: $2.5B and growing at 15% CAGR
            - Key players include major tech companies and innovative startups
            - Consumer adoption rates increasing by 25% year-over-year
            
            Competitive Landscape:
            - Established players dominate 60% of market share
            - Emerging startups gaining traction with innovative approaches
            - Regulatory environment supportive of growth
            
            Future Outlook:
            - Projected market growth of 20% annually over next 5 years
            - Technology integration driving efficiency gains
            - International expansion opportunities in European and Asian markets
            """
        elif search_depth == "comprehensive":
            base_content += f"""
            
            Detailed Market Research:
            
            Market Size & Growth:
            - Current market valuation: $2.5 billion
            - Annual growth rate: 15% CAGR
            - Projected to reach $5.2 billion by 2029
            - Key growth drivers: digital transformation, consumer demand
            
            Competitive Analysis:
            - Market leaders: 3 major companies control 60% market share
            - Mid-tier players: 15 companies with 30% combined share
            - Emerging startups: 200+ companies competing for remaining 10%
            - Average funding per startup: $2.3M in seed rounds
            
            Consumer Insights:
            - Primary demographic: 25-45 age group (65% of users)
            - Geographic distribution: 40% North America, 35% Europe, 25% Asia
            - Usage patterns: 70% daily active users, 30% weekly
            - Satisfaction scores: 4.2/5 average rating
            
            Technology Trends:
            - AI integration in 80% of new products
            - Mobile-first approach adopted by 90% of companies
            - Cloud infrastructure usage up 45% year-over-year
            - Data analytics implementation in 75% of businesses
            
            Regulatory Environment:
            - GDPR compliance required in European markets
            - Data privacy regulations tightening globally
            - Industry standards being developed by major trade associations
            - Government incentives for innovation in key regions
            """
        
        return base_content.strip()
    
    def _generate_follow_up_questions(self, query: str) -> List[str]:
        """Generate realistic follow-up questions"""
        questions = [
            f"What are the latest trends in {query}?",
            f"How is {query} impacting the industry?",
            f"What are the key challenges facing {query}?",
            f"Who are the major players in {query}?",
            f"What is the future outlook for {query}?"
        ]
        return random.sample(questions, 3)
    
    def _generate_answer(self, query: str) -> str:
        """Generate a concise answer"""
        return f"""
        {query} is a rapidly growing sector with significant market potential. 
        Recent analysis shows strong consumer demand and technological innovation 
        driving growth. Key opportunities include market expansion, technology 
        integration, and strategic partnerships.
        """.strip()
    
    def _generate_published_date(self) -> str:
        """Generate realistic published dates"""
        days_ago = random.randint(1, 30)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")
    
    def get_call_count(self) -> int:
        """Get the number of API calls made"""
        return self.call_count
    
    def reset_call_count(self):
        """Reset the call counter"""
        self.call_count = 0


# Mock Tavily client instance
mock_tavily_client = MockTavilyClient()
