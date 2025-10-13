"""
Comprehensive Mock Responses for All 17 Checkpoints
Provides realistic dummy data for testing without using OpenAI or Tavily APIs
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

class ComprehensiveMockResponses:
    """Centralized mock responses for all 17 checkpoints in the research workflow"""
    
    def __init__(self):
        self.base_timestamp = datetime.now()
        self.product_idea = "AI-powered fitness tracking app"
        self.sector = "Health & Fitness Technology"
    
    def get_mock_research_plan(self) -> Dict[str, Any]:
        """Mock research plan for research_plan_created checkpoint"""
        return {
            "sector": self.sector,
            "market_query": "AI fitness tracking app market size 2024 and wearable fitness technology trends",
            "competitor_query": "MyFitnessPal vs Fitbit vs Apple Health AI fitness apps competitors 2024",
            "customer_query": "fitness app user behavior research and what users want in fitness apps",
            "research_plan": {
                "product_idea": self.product_idea,
                "sector": self.sector,
                "research_depth": "comprehensive",
                "objectives": [
                    "Analyze market size and growth potential",
                    "Identify key competitors and their strategies", 
                    "Understand customer needs and pain points",
                    "Assess market opportunities and threats"
                ],
                "methodology": {
                    "market_analysis": "Industry reports, market research, trend analysis",
                    "competitor_analysis": "Direct competitors, feature comparison, pricing analysis",
                    "customer_analysis": "User surveys, feedback analysis, persona development"
                },
                "timeline": "2-3 weeks",
                "deliverables": [
                    "Market size and growth projections",
                    "Competitive landscape analysis", 
                    "Customer insights and personas",
                    "Strategic recommendations"
                ]
            },
            "timestamp": self.base_timestamp.isoformat(),
            "status": "research_plan_created"
        }
    
    def get_mock_queries(self) -> Dict[str, Any]:
        """Mock search queries for queries_generated checkpoint"""
        return {
            "sector": self.sector,
            "market_query": "AI fitness tracking app market size 2024 and wearable fitness technology trends",
            "competitor_query": "MyFitnessPal vs Fitbit vs Apple Health AI fitness apps competitors 2024",
            "customer_query": "fitness app user behavior research and what users want in fitness apps",
            "timestamp": (self.base_timestamp + timedelta(minutes=2)).isoformat(),
            "status": "queries_generated"
        }
    
    def get_mock_market_search_results(self) -> Dict[str, Any]:
        """Mock market search results for market_search_started/completed checkpoints"""
        return {
            "results": [
                {
                    "title": "Global Fitness App Market to Reach $15.6 Billion by 2028",
                    "url": "https://example.com/fitness-market-report-2024",
                    "content": "The global fitness app market is projected to grow from $4.2 billion in 2023 to $15.6 billion by 2028, representing a CAGR of 30.1%. Key drivers include increasing health consciousness, smartphone penetration, and AI integration in fitness tracking.",
                    "score": 0.95,
                    "published_date": "2024-01-15"
                },
                {
                    "title": "AI-Powered Fitness Apps: The Future of Personal Training",
                    "url": "https://example.com/ai-fitness-apps-trends",
                    "content": "AI integration in fitness apps is revolutionizing personal training. Machine learning algorithms can now provide personalized workout recommendations, real-time form correction, and adaptive training programs based on user performance data.",
                    "score": 0.92,
                    "published_date": "2024-02-20"
                },
                {
                    "title": "Wearable Technology and Fitness Apps Market Analysis",
                    "url": "https://example.com/wearable-fitness-market",
                    "content": "The integration of wearable devices with fitness apps is creating new opportunities. Smartwatches, fitness bands, and other wearables are generating vast amounts of health data that AI-powered apps can analyze to provide insights.",
                    "score": 0.88,
                    "published_date": "2024-03-10"
                }
            ],
            "follow_up_questions": [
                "What are the key trends in AI fitness applications?",
                "How is machine learning being used in fitness tracking?",
                "What are the privacy concerns with AI fitness apps?"
            ],
            "answer": "The AI-powered fitness tracking app market is experiencing rapid growth, driven by increasing health consciousness and technological advancement. The market is projected to reach $15.6 billion by 2028, with AI integration being a key differentiator for successful apps.",
            "timestamp": (self.base_timestamp + timedelta(minutes=5)).isoformat(),
            "status": "market_search_completed"
        }
    
    def get_mock_market_extraction_results(self) -> Dict[str, Any]:
        """Mock market extraction results for market_extraction_completed checkpoint"""
        return {
            "extracted_content": [
                {
                    "url": "https://example.com/fitness-market-report-2024",
                    "title": "Global Fitness App Market Analysis 2024",
                    "content": "Detailed market analysis showing 30.1% CAGR growth, key market segments including workout apps (45%), nutrition tracking (30%), and meditation apps (25%). North America leads with 40% market share, followed by Europe (30%) and Asia-Pacific (25%).",
                    "key_metrics": {
                        "market_size_2023": "$4.2B",
                        "projected_size_2028": "$15.6B", 
                        "cagr": "30.1%",
                        "user_base_2024": "2.8B users"
                    }
                },
                {
                    "url": "https://example.com/ai-fitness-apps-trends",
                    "title": "AI Integration in Fitness Applications",
                    "content": "AI-powered features include personalized workout generation, real-time form analysis, injury prevention, and adaptive training programs. Machine learning algorithms analyze user data to provide customized recommendations.",
                    "key_metrics": {
                        "ai_adoption_rate": "67%",
                        "user_engagement_improvement": "45%",
                        "retention_rate_ai_apps": "78%"
                    }
                }
            ],
            "timestamp": (self.base_timestamp + timedelta(minutes=8)).isoformat(),
            "status": "market_extraction_completed"
        }
    
    def get_mock_market_analysis(self) -> Dict[str, Any]:
        """Mock market analysis for market_analysis_completed checkpoint"""
        return {
            "market_analysis": {
                "market_size": {
                    "current": "$4.2 billion",
                    "projected_2028": "$15.6 billion",
                    "cagr": "30.1%"
                },
                "key_trends": [
                    "AI integration driving user engagement",
                    "Wearable device integration increasing",
                    "Personalization becoming standard expectation",
                    "Privacy and data security concerns growing"
                ],
                "market_segments": {
                    "workout_apps": {"share": "45%", "growth": "32%"},
                    "nutrition_tracking": {"share": "30%", "growth": "28%"},
                    "meditation_wellness": {"share": "25%", "growth": "35%"}
                },
                "geographic_distribution": {
                    "north_america": "40%",
                    "europe": "30%", 
                    "asia_pacific": "25%",
                    "other": "5%"
                },
                "opportunities": [
                    "AI-powered personalization",
                    "Integration with healthcare systems",
                    "Corporate wellness programs",
                    "Senior fitness market"
                ],
                "challenges": [
                    "Data privacy regulations",
                    "High user acquisition costs",
                    "Competition from established players",
                    "Technical complexity of AI features"
                ]
            },
            "timestamp": (self.base_timestamp + timedelta(minutes=12)).isoformat(),
            "status": "market_analysis_completed"
        }
    
    def get_mock_competitor_search_results(self) -> Dict[str, Any]:
        """Mock competitor search results for competitor_search_started/completed checkpoints"""
        return {
            "results": [
                {
                    "title": "MyFitnessPal vs Fitbit vs Apple Health: Complete Comparison 2024",
                    "url": "https://example.com/fitness-app-comparison",
                    "content": "Comprehensive comparison of leading fitness apps. MyFitnessPal leads in nutrition tracking with 200M+ users, Fitbit dominates wearables integration, Apple Health excels in ecosystem integration.",
                    "score": 0.94,
                    "published_date": "2024-01-20"
                },
                {
                    "title": "Top 10 AI-Powered Fitness Apps in 2024",
                    "url": "https://example.com/ai-fitness-apps-ranking",
                    "content": "Ranking of AI-powered fitness applications including Freeletics, Nike Training Club, and Strava. Analysis of AI features, user base, and market positioning.",
                    "score": 0.91,
                    "published_date": "2024-02-15"
                },
                {
                    "title": "Fitness App Market Leaders: Revenue and User Analysis",
                    "url": "https://example.com/fitness-app-leaders",
                    "content": "Market leaders analysis: MyFitnessPal ($1.2B revenue), Strava (100M users), Nike Training Club (50M downloads), and emerging AI-powered competitors.",
                    "score": 0.89,
                    "published_date": "2024-03-05"
                }
            ],
            "follow_up_questions": [
                "What are the key features of successful fitness apps?",
                "How do AI-powered fitness apps differentiate themselves?",
                "What are the pricing strategies of leading fitness apps?"
            ],
            "answer": "The fitness app market is dominated by established players like MyFitnessPal and Strava, but AI-powered apps are gaining traction with personalized features and advanced analytics.",
            "timestamp": (self.base_timestamp + timedelta(minutes=15)).isoformat(),
            "status": "competitor_search_completed"
        }
    
    def get_mock_competitor_extraction_results(self) -> Dict[str, Any]:
        """Mock competitor extraction results for competitor_extraction_completed checkpoint"""
        return {
            "extracted_content": [
                {
                    "url": "https://example.com/fitness-app-comparison",
                    "title": "Fitness App Competitive Analysis",
                    "content": "MyFitnessPal: 200M+ users, $1.2B revenue, strong nutrition tracking. Fitbit: 30M+ active users, wearables integration. Apple Health: 1B+ iOS users, ecosystem advantage. Strava: 100M users, social features.",
                    "key_metrics": {
                        "myfitnesspal_users": "200M+",
                        "fitbit_active_users": "30M+",
                        "apple_health_users": "1B+",
                        "strava_users": "100M"
                    }
                },
                {
                    "url": "https://example.com/ai-fitness-apps-ranking",
                    "title": "AI Fitness Apps Competitive Landscape",
                    "content": "Freeletics: AI workout generation, 50M users. Nike Training Club: AI coaching, 50M downloads. Strava: AI insights, premium features. Emerging players focusing on personalization.",
                    "key_metrics": {
                        "freeletics_users": "50M",
                        "nike_training_downloads": "50M",
                        "ai_feature_adoption": "67%"
                    }
                }
            ],
            "timestamp": (self.base_timestamp + timedelta(minutes=18)).isoformat(),
            "status": "competitor_extraction_completed"
        }
    
    def get_mock_competitor_analysis(self) -> Dict[str, Any]:
        """Mock competitor analysis for competitor_analysis_completed checkpoint"""
        return {
            "competitor_analysis": {
                "direct_competitors": [
                    {
                        "name": "MyFitnessPal",
                        "strengths": ["Large user base", "Nutrition tracking", "Brand recognition"],
                        "weaknesses": ["Limited AI features", "Outdated interface", "Privacy concerns"],
                        "market_share": "25%",
                        "revenue": "$1.2B"
                    },
                    {
                        "name": "Strava",
                        "strengths": ["Social features", "Community", "Premium model"],
                        "weaknesses": ["Limited to fitness", "High subscription cost", "Complex interface"],
                        "market_share": "15%",
                        "revenue": "$200M"
                    }
                ],
                "ai_powered_competitors": [
                    {
                        "name": "Freeletics",
                        "strengths": ["AI workout generation", "Personalization", "No equipment needed"],
                        "weaknesses": ["Limited nutrition tracking", "High intensity focus", "Subscription model"],
                        "market_share": "8%",
                        "revenue": "$50M"
                    },
                    {
                        "name": "Nike Training Club",
                        "strengths": ["Brand power", "Free content", "Expert trainers"],
                        "weaknesses": ["Limited AI", "Nike ecosystem only", "Basic tracking"],
                        "market_share": "12%",
                        "revenue": "$100M"
                    }
                ],
                "competitive_gaps": [
                    "Comprehensive AI personalization",
                    "Cross-platform integration",
                    "Advanced health insights",
                    "Affordable pricing model"
                ],
                "market_positioning": {
                    "premium_ai_features": "Differentiation opportunity",
                    "user_experience": "Key competitive advantage",
                    "data_privacy": "Trust and security focus",
                    "pricing": "Value-based pricing strategy"
                }
            },
            "timestamp": (self.base_timestamp + timedelta(minutes=22)).isoformat(),
            "status": "competitor_analysis_completed"
        }
    
    def get_mock_customer_search_results(self) -> Dict[str, Any]:
        """Mock customer search results for customer_search_started/completed checkpoints"""
        return {
            "results": [
                {
                    "title": "Fitness App User Behavior Study 2024",
                    "url": "https://example.com/fitness-app-user-study",
                    "content": "Comprehensive study of 10,000 fitness app users reveals key behaviors: 78% use apps for tracking, 65% want personalization, 45% struggle with motivation, 60% prefer AI recommendations.",
                    "score": 0.93,
                    "published_date": "2024-01-25"
                },
                {
                    "title": "What Users Really Want in Fitness Apps",
                    "url": "https://example.com/fitness-app-user-needs",
                    "content": "User research shows top priorities: ease of use (85%), accurate tracking (80%), motivation features (75%), social features (60%), and AI personalization (55%). Privacy concerns are growing.",
                    "score": 0.91,
                    "published_date": "2024-02-10"
                },
                {
                    "title": "Fitness App User Retention and Engagement Strategies",
                    "url": "https://example.com/fitness-app-retention",
                    "content": "Analysis of user retention patterns: 30-day retention is 45%, 90-day retention is 25%. Key factors: personalization, goal setting, social features, and AI coaching improve retention by 40%.",
                    "score": 0.88,
                    "published_date": "2024-03-01"
                }
            ],
            "follow_up_questions": [
                "What are the main pain points of fitness app users?",
                "How do users prefer to interact with AI features?",
                "What drives long-term engagement in fitness apps?"
            ],
            "answer": "Fitness app users prioritize ease of use, accurate tracking, and personalization. AI features are increasingly important, with 55% of users wanting AI recommendations. Privacy and data security are growing concerns.",
            "timestamp": (self.base_timestamp + timedelta(minutes=25)).isoformat(),
            "status": "customer_search_completed"
        }
    
    def get_mock_customer_extraction_results(self) -> Dict[str, Any]:
        """Mock customer extraction results for customer_extraction_completed checkpoint"""
        return {
            "extracted_content": [
                {
                    "url": "https://example.com/fitness-app-user-study",
                    "title": "Fitness App User Behavior Analysis",
                    "content": "Detailed user behavior analysis: 78% use apps for activity tracking, 65% want personalized recommendations, 45% struggle with motivation, 60% prefer AI-powered features. Key pain points: complex interfaces, inaccurate tracking, lack of motivation.",
                    "key_metrics": {
                        "tracking_usage": "78%",
                        "personalization_demand": "65%",
                        "motivation_struggles": "45%",
                        "ai_preference": "60%"
                    }
                },
                {
                    "url": "https://example.com/fitness-app-user-needs",
                    "title": "User Needs and Preferences in Fitness Apps",
                    "content": "User priorities ranked: ease of use (85%), accurate tracking (80%), motivation features (75%), social features (60%), AI personalization (55%). Privacy concerns increasing: 70% worry about data security.",
                    "key_metrics": {
                        "ease_of_use_priority": "85%",
                        "accurate_tracking_priority": "80%",
                        "motivation_features_priority": "75%",
                        "privacy_concerns": "70%"
                    }
                }
            ],
            "timestamp": (self.base_timestamp + timedelta(minutes=28)).isoformat(),
            "status": "customer_extraction_completed"
        }
    
    def get_mock_customer_analysis(self) -> Dict[str, Any]:
        """Mock customer analysis for customer_analysis_completed checkpoint"""
        return {
            "customer_analysis": {
                "user_personas": [
                    {
                        "name": "Fitness Enthusiast",
                        "demographics": "25-35, urban, high income",
                        "needs": ["Advanced tracking", "AI recommendations", "Social features"],
                        "pain_points": ["Complex interfaces", "Limited personalization"],
                        "behavior": "Daily app usage, premium features willing"
                    },
                    {
                        "name": "Health Beginner",
                        "demographics": "30-45, suburban, middle income", 
                        "needs": ["Simple interface", "Motivation", "Education"],
                        "pain_points": ["Overwhelming features", "Lack of guidance"],
                        "behavior": "Intermittent usage, free features preferred"
                    },
                    {
                        "name": "Data-Driven User",
                        "demographics": "28-40, tech-savvy, high income",
                        "needs": ["Detailed analytics", "AI insights", "Integration"],
                        "pain_points": ["Limited data export", "Poor AI quality"],
                        "behavior": "Regular usage, premium features willing"
                    }
                ],
                "key_insights": [
                    "78% of users want accurate tracking",
                    "65% demand personalization features", 
                    "60% prefer AI-powered recommendations",
                    "70% have privacy concerns",
                    "45% struggle with motivation"
                ],
                "pain_points": [
                    "Complex user interfaces",
                    "Inaccurate tracking data",
                    "Lack of motivation features",
                    "Privacy and data security concerns",
                    "Limited personalization"
                ],
                "opportunities": [
                    "AI-powered personalization",
                    "Simplified user experience",
                    "Enhanced privacy features",
                    "Motivation and gamification",
                    "Cross-platform integration"
                ]
            },
            "timestamp": (self.base_timestamp + timedelta(minutes=32)).isoformat(),
            "status": "customer_analysis_completed"
        }
    
    def get_mock_report_generation_data(self) -> Dict[str, Any]:
        """Mock data for report_generation_started/completed checkpoints"""
        return {
            "report_data": {
                "executive_summary": {
                    "market_opportunity": "The AI-powered fitness tracking app market presents a $15.6B opportunity by 2028, with 30.1% CAGR growth driven by increasing health consciousness and AI integration.",
                    "competitive_landscape": "Market dominated by MyFitnessPal (25% share) and Strava (15% share), but AI-powered apps like Freeletics are gaining traction with personalized features.",
                    "customer_insights": "78% of users want accurate tracking, 65% demand personalization, and 60% prefer AI recommendations. Privacy concerns are growing at 70%.",
                    "recommendations": "Focus on AI-powered personalization, simplified UX, enhanced privacy, and competitive pricing to capture market share."
                },
                "market_analysis": {
                    "market_size": "$4.2B current, $15.6B projected 2028",
                    "growth_rate": "30.1% CAGR",
                    "key_segments": "Workout apps (45%), Nutrition (30%), Wellness (25%)",
                    "geographic_distribution": "North America (40%), Europe (30%), Asia-Pacific (25%)"
                },
                "competitive_analysis": {
                    "market_leaders": "MyFitnessPal ($1.2B revenue), Strava (100M users)",
                    "ai_competitors": "Freeletics (50M users), Nike Training Club (50M downloads)",
                    "competitive_gaps": "Comprehensive AI personalization, cross-platform integration, advanced health insights"
                },
                "customer_analysis": {
                    "key_personas": "Fitness Enthusiast, Health Beginner, Data-Driven User",
                    "user_needs": "Accurate tracking (78%), Personalization (65%), AI features (60%)",
                    "pain_points": "Complex interfaces, inaccurate tracking, lack of motivation, privacy concerns"
                }
            },
            "timestamp": (self.base_timestamp + timedelta(minutes=35)).isoformat(),
            "status": "report_generation_completed"
        }
    
    def get_mock_final_report(self) -> Dict[str, Any]:
        """Mock final report for final_report_delivered checkpoint"""
        return {
            "mock": True,
            "title": "AI-Powered Fitness Tracking App: Market Research Report",
            "executive_summary": {
                "market_opportunity": "The AI-powered fitness tracking app market presents a significant $15.6B opportunity by 2028, with 30.1% CAGR growth driven by increasing health consciousness and AI integration.",
                "competitive_landscape": "Market dominated by established players like MyFitnessPal (25% share) and Strava (15% share), but AI-powered apps are gaining traction with personalized features and advanced analytics.",
                "customer_insights": "User research reveals 78% want accurate tracking, 65% demand personalization, and 60% prefer AI recommendations. Privacy concerns are growing at 70%.",
                "strategic_recommendations": "Focus on AI-powered personalization, simplified user experience, enhanced privacy features, and competitive pricing to capture market share.",
                "confidence_level": "Medium"
            },
            "market_analysis": {
                "market_size": {
                    "current": "$4.2 billion",
                    "projected_2028": "$15.6 billion",
                    "cagr": "30.1%"
                },
                "key_trends": [
                    "AI integration driving user engagement",
                    "Wearable device integration increasing", 
                    "Personalization becoming standard expectation",
                    "Privacy and data security concerns growing"
                ],
                "market_segments": {
                    "workout_apps": {"share": "45%", "growth": "32%"},
                    "nutrition_tracking": {"share": "30%", "growth": "28%"},
                    "meditation_wellness": {"share": "25%", "growth": "35%"}
                }
            },
            "competitive_analysis": {
                "direct_competitors": [
                    {
                        "name": "MyFitnessPal",
                        "market_share": "25%",
                        "revenue": "$1.2B",
                        "strengths": ["Large user base", "Nutrition tracking", "Brand recognition"],
                        "weaknesses": ["Limited AI features", "Outdated interface", "Privacy concerns"]
                    },
                    {
                        "name": "Strava", 
                        "market_share": "15%",
                        "revenue": "$200M",
                        "strengths": ["Social features", "Community", "Premium model"],
                        "weaknesses": ["Limited to fitness", "High subscription cost", "Complex interface"]
                    }
                ],
                "ai_powered_competitors": [
                    {
                        "name": "Freeletics",
                        "market_share": "8%",
                        "revenue": "$50M", 
                        "strengths": ["AI workout generation", "Personalization", "No equipment needed"],
                        "weaknesses": ["Limited nutrition tracking", "High intensity focus", "Subscription model"]
                    }
                ],
                "competitive_gaps": [
                    "Comprehensive AI personalization",
                    "Cross-platform integration", 
                    "Advanced health insights",
                    "Affordable pricing model"
                ]
            },
            "customer_analysis": {
                "user_personas": [
                    {
                        "name": "Fitness Enthusiast",
                        "demographics": "25-35, urban, high income",
                        "needs": ["Advanced tracking", "AI recommendations", "Social features"],
                        "pain_points": ["Complex interfaces", "Limited personalization"]
                    },
                    {
                        "name": "Health Beginner",
                        "demographics": "30-45, suburban, middle income",
                        "needs": ["Simple interface", "Motivation", "Education"],
                        "pain_points": ["Overwhelming features", "Lack of guidance"]
                    }
                ],
                "key_insights": [
                    "78% of users want accurate tracking",
                    "65% demand personalization features",
                    "60% prefer AI-powered recommendations", 
                    "70% have privacy concerns",
                    "45% struggle with motivation"
                ]
            },
            "pmf_assessment": {
                "market_opportunities": [
                    "Large and growing fitness app market ($15.6B by 2028)",
                    "High demand for AI-powered personalization features",
                    "Growing health consciousness and fitness tracking adoption",
                    "Integration opportunities with wearable devices and health platforms"
                ],
                "product_fit_score": "72% - Strong market signals but competitive landscape requires differentiation",
                "key_risks": [
                    "Highly competitive market with established players",
                    "User acquisition costs may be high due to market saturation",
                    "Privacy concerns could limit adoption",
                    "Need to continuously innovate to maintain competitive advantage"
                ],
                "success_probability": "Medium - Good market opportunity but requires strong execution and differentiation",
                "time_to_market": "6-12 months for MVP, 12-18 months for full feature set"
            },
            "strategic_recommendations": {
                "product_strategy": [
                    "Focus on AI-powered personalization as key differentiator",
                    "Implement simplified, intuitive user interface",
                    "Develop comprehensive privacy and security features",
                    "Create flexible pricing tiers for different user segments"
                ],
                "market_entry": [
                    "Target fitness enthusiasts and data-driven users initially",
                    "Emphasize AI personalization in marketing messaging",
                    "Partner with fitness influencers and health professionals",
                    "Offer freemium model with premium AI features"
                ],
                "competitive_positioning": [
                    "Position as the most intelligent and personalized fitness app",
                    "Highlight superior AI capabilities vs. established competitors",
                    "Emphasize privacy and data security advantages",
                    "Focus on user experience and ease of use"
                ]
            },
            "timestamp": (self.base_timestamp + timedelta(minutes=40)).isoformat(),
            "status": "final_report_delivered"
        }
    
    def get_mock_response_for_checkpoint(self, checkpoint: str) -> Dict[str, Any]:
        """Get mock response for specific checkpoint"""
        checkpoint_responses = {
            "research_plan_created": self.get_mock_research_plan(),
            "queries_generated": self.get_mock_queries(),
            "market_search_started": {"status": "market_search_started", "timestamp": (self.base_timestamp + timedelta(minutes=3)).isoformat()},
            "market_search_completed": self.get_mock_market_search_results(),
            "market_extraction_completed": self.get_mock_market_extraction_results(),
            "market_analysis_completed": self.get_mock_market_analysis(),
            "competitor_search_started": {"status": "competitor_search_started", "timestamp": (self.base_timestamp + timedelta(minutes=13)).isoformat()},
            "competitor_search_completed": self.get_mock_competitor_search_results(),
            "competitor_extraction_completed": self.get_mock_competitor_extraction_results(),
            "competitor_analysis_completed": self.get_mock_competitor_analysis(),
            "customer_search_started": {"status": "customer_search_started", "timestamp": (self.base_timestamp + timedelta(minutes=23)).isoformat()},
            "customer_search_completed": self.get_mock_customer_search_results(),
            "customer_extraction_completed": self.get_mock_customer_extraction_results(),
            "customer_analysis_completed": self.get_mock_customer_analysis(),
            "report_generation_started": {"status": "report_generation_started", "timestamp": (self.base_timestamp + timedelta(minutes=33)).isoformat()},
            "report_generation_completed": self.get_mock_report_generation_data(),
            "final_report_delivered": self.get_mock_final_report()
        }
        
        return checkpoint_responses.get(checkpoint, {"status": checkpoint, "timestamp": self.base_timestamp.isoformat()})

# Global instance for easy access
comprehensive_mock_responses = ComprehensiveMockResponses()
