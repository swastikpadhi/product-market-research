# Product-Market Fit Research Assistant

An AI-powered platform that conducts comprehensive market research to validate product ideas and assess product-market fit using multi-agent orchestration.

## 🎯 Overview

This application uses LangGraph to orchestrate multiple AI agents that perform market analysis, competitor research, and customer insights gathering. The system generates detailed research reports with actionable recommendations for product development and market entry strategies.

## ✨ Key Features

- **Multi-Agent Research**: Orchestrated AI agents for market, competitor, and customer analysis
- **Real-time Progress Tracking**: Live updates on research progress with 17 checkpoints
- **Comprehensive Reports**: Detailed insights with citations and strategic recommendations
- **Credit System**: Usage-based pricing with limits
- **Export Functionality**: Download research reports
- **Responsive UI**: Modern React interface with real-time updates

## 🏗️ Architecture

- **Backend**: FastAPI + Celery + LangGraph on EC2 with Docker
- **Frontend**: React app with Tailwind CSS
- **Databases**: PostgreSQL (Neon) + MongoDB (Atlas) + Redis (Redis Cloud)
- **AI**: OpenAI GPT-4 + Tavily Search API
- **Deployment**: See TECHNICAL_DOCUMENTATION.md for deployment details

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL, MongoDB, Redis

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set up environment variables
cp env.prod.template .env
# Edit .env with your API keys and database URLs

# Initialize database
psql "postgresql://user:pass@host:5432/dbname" -f database_schema.sql

# Start services
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Environment Variables

**Backend (.env):**
```bash
# Environment
ENVIRONMENT=[production|development]

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
HCAPTCHA_SECRET=your_hcaptcha_secret_here
AUTH_KEY=your_auth_key_here

# Database URLs (Cloud Services)
POSTGRES_URL=postgresql+asyncpg://username:password@your-neon-host:5432/database_name
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database_name
REDIS_URL=redis://username:password@your-redis-cloud-host:6379

# API Configuration
API_HOST=0.0.0.0
PORT=8000

# Celery Configuration (optional - will use Redis URLs if not set)
CELERY_BROKER_URL=redis://your-redis-host:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-host:6379/0

# Logging Configuration
LOG_FILE=backend_server.log
CELERY_LOG_FILE=celery_worker.log
LOG_LEVEL=INFO
```

**Frontend Configuration:**
The frontend automatically reads backend configuration through the `start.sh` script.

## 📖 Usage

### 1. Submit Research Request

Enter your product idea and select research depth:
- **Essential**: Fast validation with key insights
- **Standard**: Detailed analysis with strategic recommendations  
- **Deep**: Comprehensive intelligence with in-depth analysis

### 2. Monitor Progress

Track research progress through 17 checkpoints:
- Research plan creation
- Query generation
- Market/competitor/customer searches
- Data extraction and analysis
- Report generation

### 3. View Results

Access comprehensive reports with:
- Executive summary
- Market insights and trends
- Competitive landscape analysis
- Customer pain points and needs
- Product-market fit assessment
- Strategic recommendations
- Source citations

## 📁 Project Structure

```
product-market-research/
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── core/              # Core utilities and config
│   │   │   ├── langgraph/     # LangGraph agents and supervisor
│   │   │   └── prompts.py     # Centralized AI prompts
│   │   ├── db/                # Database managers
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── worker/            # Celery tasks
│   │   └── mocks/             # Development mocks
│   ├── main.py                # FastAPI application
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── research/      # Research-related components
│   │   │   ├── report/        # Report display components
│   │   │   └── ui/            # Reusable UI components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── utils/             # Utility functions
│   │   └── config/            # Configuration
│   └── package.json           # Node.js dependencies
└── README.md                  # This file
```

## 🔧 Development

### Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload

# Run Celery worker
celery -A app.worker.celery_app worker --loglevel=info
```

### Frontend Development

```bash
# Install dependencies
npm install

# Run linter
npm run lint

# Start development server
npm start
```


## 📊 Research Depth Options

|   Depth   |              Description               |  Duration  |   Credits  |
|-----------|----------------------------------------|------------|------------|
| Essential | Fast validation with key insights      | ~1 minutes | 6 credits  |
| Standard  | Detailed analysis with recommendations | ~2 minutes | 12 credits |
| Deep      | Comprehensive intelligence             | ~3 minutes | 18 credits |

## 🔍 Example Research Output

The system generates reports with:
- **Market Size**: Current and projected market values
- **Growth Trends**: Industry growth rates and drivers
- **Competitors**: Key players, pricing, positioning
- **Customer Insights**: Pain points, needs, segments
- **Product-Market Fit**: Fit score and success probability
- **Recommendations**: Strategic actions and next steps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions or issues:
- Check the technical documentation
- Review the codebase structure
- Open an issue on GitHub