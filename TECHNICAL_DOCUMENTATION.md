# Technical Documentation

## System Architecture Overview

The Product-Market Fit Research Assistant is a multi-agent AI system built on LangGraph that orchestrates specialized agents to conduct comprehensive market research. The system uses a microservices architecture with FastAPI backend, React frontend, and multiple database systems.

### System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                           PRODUCT-MARKET FIT RESEARCH ASSISTANT        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐    │
│  │   REACT SPA     │    │   NGINX PROXY   │    │   FASTAPI API    │    │
│  │                 │    │                 │    │                  │    │
│  │ • Research Form │◄──►│ • Static Files  │◄──►│ • REST Routes    │    │
│  │ • Progress UI   │    │ • API Routing   │    │ • Auth & Credits │    │
│  │ • Report Display│    │ • SSL/TLS       │    │ • hCaptcha       │    │
│  │ • Real-time     │    │ • Load Balance  │    │ • Task Management│    │
│  │   Polling       │    │                 │    │                  │    │
│  └─────────────────┘    └─────────────────┘    └──────────────────┘    │
│  -------------------------------------------------------------------   │      
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │   CELERY        │    │   LANGGRAPH     │    │   AI AGENTS     │     │
│  │   WORKER        │    │   SUPERVISOR    │    │                 │     │
│  │                 │    │                 │    │ • Market Agent  │     │
│  │ • Task Queue    │◄──►│ • State Graph   │◄──►│ • Competitor    │     │
│  │ • Background    │    │ • Workflow      │    │   Agent         │     │
│  │   Processing    │    │   Orchestration │    │ • Customer      │     │
│  │ • Progress      │    │ • Node Routing  │    │   Agent         │     │
│  │   Updates       │    │                 │    │ • Report Agent  │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│  ------------------------------------------------------------------    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │   DATABASES     │    │   EXTERNAL      │    │   PROGRESS      │     │
│  │                 │    │   SERVICES      │    │   TRACKING      │     │
│  │ • PostgreSQL    │    │                 │    │                 │     │
│  │   (Neon)        │    │ • OpenAI GPT-4  │    │ • Redis Cache   │     │
│  │ • MongoDB       │    │ • Tavily Search │    │ • Status Updates│     │
│  │   (Atlas)       │    │ • hCaptcha      │    │ • Checkpoints   │     │
│  │ • Redis         │    │                 │    │ • Real-time     │     │
│  │   (Redis Cloud) │    │                 │    │   Notifications │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### System Components

**Frontend Layer:**
- **React SPA** - Modern single-page application with real-time updates
- **Tailwind CSS** - Utility-first CSS framework for responsive design
- **Custom Hooks** - State management for research tasks and progress
- **Export Utilities** - Report download functionality
- **Search Interface** - As-you-type suggestions and task filtering
- **Progress Tracking** - Live updates with checkpoint visualization
- **Credit Display** - Searches remaining counter for user awareness

**API Gateway Layer:**
- **Nginx Reverse Proxy** - Static file serving and API routing
- **SSL/TLS Termination** - Let's Encrypt certificates with auto-renewal
- **Load Balancing** - Request distribution
- **Rate Limiting** - Request throttling and abuse prevention
- **Static File Serving** - Frontend files served directly from Nginx

**Backend Services Layer:**
- **FastAPI Application** - RESTful API with async support
- **Celery Task Queue** - Background job processing
- **LangGraph Supervisor** - Multi-agent orchestration
- **Credit Management** - Usage tracking and billing
- **Authentication** - Auth key validation and hCaptcha verification
- **Progress Tracking** - Lightweight checkpoint system for real-time updates

**AI Agent Layer:**
- **Market Analysis Agent** - Market size, trends, and opportunities
- **Competitor Analysis Agent** - Competitive landscape analysis
- **Customer Insights Agent** - Customer pain points and needs
- **Report Generation Agent** - Final report synthesis

**Data Layer:**
- **PostgreSQL (Neon)** - Structured data (credits, transactions)
- **MongoDB (Atlas)** - Unstructured research results
- **Redis (Redis Cloud)** - Caching and task queue broker

**External Services:**
- **OpenAI GPT-4** - Language model for analysis
- **Tavily Search API** - Web search and data collection
- **hCaptcha** - Bot protection and verification

### Research Request Flow

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              RESEARCH REQUEST FLOW                             │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  1. REQUEST SUBMISSION & VALIDATION                                            │
│     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│     │   React     │───►│   FastAPI   │───►│   Verify    │───►│   Credit    │   │
│     │   Frontend  │    │   Router    │    │  hCaptcha   │    │ Validation  │
│     └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                                                │
│  2. TASK CREATION & QUEUE SUBMISSION                                           │
│     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│     │   Research  │───►│   MongoDB   │───►│   Celery    │───►│   Redis     │   │
│     │   Service   │    │  (Task)     │    │  (Queue)    │    │ (Broker)    │   │
│     └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                                                │
│  3. LANGGRAPH WORKFLOW EXECUTION                                               │
│     ┌─────────────┐                                                            │
│     │  Supervisor │───► Parse Product Idea & Generate Queries                  │
│     │    Node     │                                                            │
│     └─────────────┘                                                            │
│           │                                                                    │
│           ▼                                                                    │
│     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│     │  Parallel   │───►│   Market    │    │ Competitor  │                      │
│     │  Analysis   │    │   Agent     │    │   Agent     │                      │
│     │    Node     │    │             │    │             │                      │
│     └─────────────┘    └─────────────┘    └─────────────┘                      │
│           │                     │           │                                  │
│           │                     ▼           ▼                                  │
│           │              ┌───────────────────┐                                 │
│           │              │   Tavily          │                                 │
│           │              │   Search/Extract  │                                 │
│           │              └───────────────────┘                                 │
│           │                                                                    │
│           ▼                                                                    │
│     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│     │  Customer   │    │   Report    │    │   OpenAI    │                      │
│     │   Agent     │───►│ Generation  │───►│   GPT-4     │                      │
│     │             │    │    Node     │    │             │                      │
│     └─────────────┘    └─────────────┘    └─────────────┘                      │
│                                                                                │
│  4. PROGRESS TRACKING & STORAGE                                                │
│     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│     │   Progress  │───►│   Redis     │───►│   MongoDB   │───►│ PostgreSQL  │   │
│     │   Tracker   │    │  (Cache)    │    │ (Results)   │    │ (Credits)   │   │
│     └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                                                │
│  5. REAL-TIME UPDATES TO FRONTEND                                              │
│     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│     │   Frontend  │◄───│   FastAPI   │◄───│   Redis     │                      │
│     │   Polling   │    │   Status    │    │  (Progress) │                      │
│     └─────────────┘    └─────────────┘    └─────────────┘                      │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

**Backend Services:**
- FastAPI application server
- Celery task queue for background processing
- LangGraph multi-agent orchestration
- Database abstraction layer
- Credit management system

**Frontend Features:**
- **React SPA** - Single-page application with real-time updates
- **Search Interface** - As-you-type suggestions and task filtering
- **Progress Tracking** - Live updates with lightweight checkpoint system
- **Credit Display** - Searches remaining counter for user awareness
- **Export Functionality** - Comprehensive report downloads
- **Responsive Design** - Tailwind CSS for mobile and desktop

### Frontend Search & Filtering

**As-You-Type Search:**
- Real-time search suggestions
- Task filtering by status and date
- Search across task content and results
- Debounced input for performance

**Task Management:**
- Filter by research depth (Essential, Standard, Deep)
- Sort by creation date, status, or completion time
- Pagination for large task lists
- Bulk operations support

### Progress Tracking System

**Lightweight Checkpoint Logic:**
- **17 Checkpoints** - Granular progress tracking through research workflow
- **Real-time Updates** - Live progress updates via Redis
- **Status Visualization** - Visual progress indicators
- **Error Handling** - Graceful failure and retry mechanisms

**Checkpoint Categories:**
1. **Initialization** - Request validation and setup
2. **Query Generation** - Search query creation
3. **Market Analysis** - Market research execution
4. **Competitor Analysis** - Competitive landscape research
5. **Customer Insights** - Customer analysis and personas
6. **Report Generation** - Final report synthesis
7. **Completion** - Results storage and cleanup

**Databases:**
- PostgreSQL: Structured data (credit transactions)
- MongoDB: Unstructured research results
- Redis: Caching and task queue broker

### Research Depth Configuration

**Essential Research (6 credits):**
- **Duration**: ~1 minute
- **Tavily Search Calls**: 3 calls (1 per agent: Market, Competitor, Customer)
- **Tavily Extract Calls**: 3 calls (1 per agent)
- **Search Depth**: "basic" - Standard web search
- **Extract Depth**: "basic" - Basic content extraction
- **URLs Extracted**: 5 URLs per agent (15 total)
- **Max Sources**: 20 per search
- **Use Case**: Quick validation and initial insights

**Standard Research (12 credits):**
- **Duration**: ~2 minutes
- **Tavily Search Calls**: 3 calls (1 per agent: Market, Competitor, Customer)
- **Tavily Extract Calls**: 3 calls (1 per agent)
- **Search Depth**: "advanced" - Comprehensive web search with deeper results
- **Extract Depth**: "advanced" - Advanced content extraction with full page content
- **URLs Extracted**: 5 URLs per agent (15 total)
- **Max Sources**: 20 per search
- **Use Case**: Detailed market research with strategic insights

**Deep Research (18 credits):**
- **Duration**: ~3 minutes
- **Tavily Search Calls**: 3 calls (1 per agent: Market, Competitor, Customer)
- **Tavily Extract Calls**: 3 calls (1 per agent)
- **Search Depth**: "advanced" - Comprehensive web search with deeper results
- **Extract Depth**: "advanced" - Advanced content extraction with full page content
- **URLs Extracted**: 10 URLs per agent (30 total)
- **Max Sources**: 20 per search
- **Use Case**: Enterprise-level research with extensive citations

**Tavily API Usage Details:**

**Search Depth Differences:**
- **Basic Search**: Standard web search with surface-level results
- **Advanced Search**: Comprehensive search with deeper web crawling and more relevant results

**Extract Depth Differences:**
- **Basic Extract**: Extracts main content and key information from pages
- **Advanced Extract**: Full page content extraction including detailed text, metadata, and comprehensive information

**Research Depth Comparison:**

| Depth | Credits | Duration | Search Calls | Extract Calls | URLs Extracted | Search Depth | Extract Depth | Use Case |
|-------|---------|----------|--------------|---------------|----------------|--------------|---------------|----------|
| Essential | 6 | ~1 min | 3 | 3 | 15 | basic | basic | Quick validation |
| Standard | 12 | ~2 min | 3 | 3 | 15 | advanced | advanced | Strategic planning |
| Deep | 18 | ~3 min | 3 | 3 | 30 | advanced | advanced | Enterprise research |

## LangGraph Agent Architecture

### Research Supervisor

The ResearchSupervisor orchestrates the entire research workflow using LangGraph's StateGraph. It manages state transitions and coordinates between specialized agents.

**State Management:**
- ResearchState tracks progress through 17 checkpoints
- State transitions: initialization → planning → execution → completion
- Error handling with state rollback capabilities

**Workflow Orchestration:**
1. Parse product idea and generate research plan
2. Create search queries for market, competitor, and customer research
3. Execute parallel searches using Tavily API
4. Coordinate agent analysis
5. Generate final report

### Specialized Agents

**Market Analysis Agent:**
- Analyzes market size, growth trends, and opportunities
- Processes search results and extracts key insights
- Generates market-specific recommendations
- Tracks citations for all claims

**Competitor Analysis Agent:**
- Identifies key competitors and market leaders
- Analyzes pricing strategies and positioning
- Identifies competitive gaps and opportunities
- Assesses market saturation levels

**Customer Insights Agent:**
- Analyzes customer pain points and needs
- Identifies target customer segments
- Evaluates satisfaction drivers and priorities
- Generates customer-centric recommendations

**Report Generation Agent:**
- Synthesizes insights from all analysis agents
- Aggregates and deduplicates citations
- Generates comprehensive final report
- Ensures consistent formatting and structure

## Database Schema

### PostgreSQL Schema

**Credit Balances Table:**
```sql
CREATE TABLE credit_balances (
    id UUID PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    month_year VARCHAR(7) NOT NULL,
    current_balance INTEGER NOT NULL,
    monthly_limit INTEGER DEFAULT 1000,
    total_used_this_month INTEGER DEFAULT 0,
    total_researches_this_month INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);
```

**Credit Transactions Table:**
```sql
CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE,
    balance_id UUID REFERENCES credit_balances(id),
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    research_request_id VARCHAR(100),
    research_depth VARCHAR(20)
);
```

### MongoDB Schema

**Research Tasks Collection:**
- Stores unstructured research results
- Tracks task status and progress
- Maintains research data and final reports
- Supports complex nested document structures
- Powers free text queries on report titles

## API Architecture

### FastAPI Endpoints

**Research Management:**
- `POST /api/v1/research/submit` - Submit research request
- `GET /api/v1/research/tasks` - List research tasks
- `GET /api/v1/research/tasks/{id}` - Get specific task
- `DELETE /api/v1/research/tasks/{id}` - Delete task
- `POST /api/v1/research/tasks/{id}/abort` - Abort running task

**Report Access:**
- `GET /api/v1/research/tasks/{id}/report` - Get research report
- `GET /api/v1/research/tasks/{id}/export` - Export report data (download powered by frontend)

**System Health:**
- `GET /health` - Health check with dependency status

### Request/Response Schemas

**Research Request:**
```python
class ResearchRequest(BaseModel):
    product_idea: str
    research_depth: str  # basic, standard, comprehensive
    auth_key: str
```

**Research Response:**
```python
class ResearchResponse(BaseModel):
    request_id: str
    status: str
    message: str
```

## Celery Task Processing

### Task Queue Architecture

**Task Definition:**
- `process_research_task` - Main research orchestration
- Async execution with progress tracking
- Error handling and retry mechanisms
- State persistence across worker restarts

**Worker Configuration:**
- Redis as message broker
- Multiple worker processes
- Task routing and prioritization
- Monitoring and logging



## Frontend Architecture

### React Component Structure

**Research Components:**
- `ResearchForm` - Product idea submission
- `ActiveResearchProgress` - Real-time progress tracking
- `ResearchTaskList` - Task management interface
- `ResearchTaskCard` - Individual task display

**Report Components:**
- `ReportSummaryCards` - Key metrics display
- `ReportTabNavigation` - Report section navigation
- Tab components for different report sections

**UI Components:**
- Reusable components with Tailwind CSS
- Radix UI primitives for accessibility
- Custom hooks for state management
- Export utilities for report downloads

### State Management

**Custom Hooks:**
- `useAppState` - Global application state
- `useResearchTasks` - Task management logic
- `useSearchesRemaining` - Credit balance tracking

**Real-time Updates:**
- Polling for task status updates
- Progress tracking with visual indicators
- Error handling and user feedback

## Deployment Architecture

### Production Environment

**Backend Deployment:**
- Docker containers on EC2
- Nginx reverse proxy
- SSL termination
- Health checks and monitoring

**Frontend Deployment:**
- Static files served from EC2 via Nginx
- React build process with production optimization
- Nginx reverse proxy for API routing
- Frontend files deployed via SCP to EC2
- Single EC2 instance deployment

**Database Setup:**
- PostgreSQL (Neon) for structured data
- MongoDB (Atlas) for research results
- Redis (Redis Cloud) for caching and queues
- Connection pooling and optimization

### CI/CD Pipeline

**Backend Pipeline:**
- GitHub Actions workflow with dependency caching
- Multi-stage Docker build with intermediate layer caching
- Python dependencies cached in separate layer for faster rebuilds
- Container registry push to GitHub Container Registry (GHCR)
- EC2 deployment with docker-compose
- Nginx configuration with dynamic port replacement
- Health check validation and service restart

**Frontend Pipeline:**
- Node.js dependency caching for faster builds
- React build process with optimized production bundle
- Static files deployed directly to EC2 via SCP
- Files served from EC2 via Nginx reverse proxy

### Nginx Configuration

**Static File Serving:**
```nginx
# Frontend static files
location / {
    root /var/www/frontend;
    try_files $uri $uri/ /index.html;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# API routing
location /api/ {
    proxy_pass http://api_backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Rate Limiting Configuration:**
- **API Endpoints**: 10 requests per second with burst capacity of 20
- **Research Endpoints**: 2 requests per second with burst capacity of 5
- **IP-based Throttling**: Rate limits applied per client IP address
- **Burst Handling**: Allows temporary spikes while maintaining overall limits
- **Nodelay Policy**: Immediate rejection when limits exceeded

### Report Components

**Downloaded Report Structure:**
- **Executive Summary** - High-level insights and recommendations
- **Market Analysis** - Market size, trends, and opportunities
- **Competitive Landscape** - Key competitors and market positioning
- **Customer Insights** - Target audience and pain points
- **Product-Market Fit Score** - Quantitative PMF assessment
- **Strategic Recommendations** - Actionable next steps
- **Citations** - Source links and references
- **Methodology** - Research approach and data sources

**Report Formats:**
- **Markdown** - Documentation format for easy reading and sharing

### Credit System & Usage Tracking

**Credit Management:**
- **Usage-based Pricing** - Credits deducted per research request
- **Real-time Tracking** - Live credit balance updates
- **Searches Remaining** - User-friendly credit display
- **Credit Validation** - Pre-request credit verification

**Credit Display Features:**
- **Current Balance** - Real-time credit count
- **Searches Remaining** - Calculated based on current balance
- **Research Cost Preview** - Cost display before submission
- **Usage History** - Transaction log and credit usage

**Credit Calculation Logic:**
- **Searches Remaining**: Calculated by dividing current credits by research cost
- **Affordability Check**: Validates if user has sufficient credits before submission
- **Cost Preview**: Displays required credits and remaining searches to user
- **Real-time Updates**: Credit balance updated immediately after each research request
- **Validation**: Server-side credit verification prevents insufficient balance submissions

## Security Considerations

### API Security

**Authentication & Bot Protection:**
- **Auth Key Validation** - Mandatory API key verification
- **hCaptcha Integration** - Bot protection for all research requests
- **Request Sanitization** - Comprehensive input validation
- **CORS Configuration** - Cross-origin request security


**Data Protection:**
- **Input Validation** - Comprehensive sanitization
- **SQL Injection Prevention** - Parameterized queries
- **XSS Protection** - Output encoding and validation
- **Secure Environment Variables** - Encrypted configuration

### SSL/TLS Security

**Let's Encrypt Integration:**
- **Automated Certificates** - Free SSL certificates via Let's Encrypt
- **Auto-Renewal** - Certbot integration for automatic certificate renewal
- **Certificate Monitoring** - Automated renewal alerts and health checks
- **HTTPS Enforcement** - Secure communication enforcement

**Certificate Management:**
```bash
# Certificate installation
certbot --nginx -d yourdomain.com

# Auto-renewal setup
crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet

# Certificate status check
certbot certificates
```

### Infrastructure Security

**Network Security:**
- **VPC Configuration** - Isolated network environment
- **Security Group Rules** - Firewall rules for service access
- **Database Access Controls** - Restricted database connections

**Application Security:**
- Code quality checks
- Security headers
- Error message sanitization

## Monitoring and Logging

### Application Monitoring

**Health Checks:**
- Database connectivity
- External API availability

**Logging Strategy:**
- Structured logging with levels
- Request/response logging
- Error tracking

## Docker Compose Scaling

### Zero-Downtime Scaling Strategies

The production system supports horizontal scaling of services while maintaining zero downtime through rolling updates and load balancing.

#### 1. API Service Scaling

**Scale Up API Instances:**
```bash
# Scale research-api to 3 instances
docker compose -f docker-compose.prod.yml up -d --scale research-api=3

# Verify scaling
docker compose -f docker-compose.prod.yml ps
```

**Scale Down API Instances:**
```bash
# Scale down to 2 instances
docker compose -f docker-compose.prod.yml up -d --scale research-api=2

# Scale down to 1 instance
docker compose -f docker-compose.prod.yml up -d --scale research-api=1
```

#### 2. Celery Worker Scaling

**Scale Up Workers:**
```bash
# Scale workers to 3 instances
docker compose -f docker-compose.prod.yml up -d --scale worker=3

# Monitor worker queues
docker compose -f docker-compose.prod.yml logs -f worker
```

**Scale Down Workers:**
```bash
# Gracefully scale down workers
docker compose -f docker-compose.prod.yml up -d --scale worker=2

# Stop specific worker
docker compose -f docker-compose.prod.yml stop research_worker_prod_2
```

#### 3. Rolling Updates

**Update API Service:**
```bash
# Pull latest image
docker compose -f docker-compose.prod.yml pull research-api

# Rolling update with zero downtime
docker compose -f docker-compose.prod.yml up -d --no-deps research-api

# Verify health
docker compose -f docker-compose.prod.yml ps
```

**Update Worker Service:**
```bash
# Pull latest image
docker compose -f docker-compose.prod.yml pull worker

# Rolling update
docker compose -f docker-compose.prod.yml up -d --no-deps worker
```

### Load Balancing Configuration

#### Nginx Load Balancing Setup

Update `nginx.conf` for multiple API instances:

```nginx
upstream api_backend {
    server research_api_prod_1:8000;
    server research_api_prod_2:8000;
    server research_api_prod_3:8000;
}

server {
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Health Check Integration

**API Health Monitoring:**
```bash
# Check API health across instances
curl http://localhost/api/v1/health

# Monitor specific instance
curl http://localhost:8000/health
```

**Worker Health Monitoring:**
```bash
# Check worker status
docker compose -f docker-compose.prod.yml exec worker celery -A app.worker.celery_app inspect active

# Monitor queue lengths
docker compose -f docker-compose.prod.yml exec worker celery -A app.worker.celery_app inspect stats
```

### Resource Management

#### Memory Limits

**Current Configuration:**
- **API Service**: 200M limit, 100M reservation
- **Worker Service**: 1.2G limit, 800M reservation  
- **Nginx**: 32M limit, 16M reservation

**Scaling Considerations:**
```bash
# Monitor resource usage
docker stats

# Adjust memory limits in docker-compose.prod.yml
deploy:
  resources:
    limits:
      memory: 400M  # Increase for high load
    reservations:
      memory: 200M
```

#### CPU Scaling

**Multi-Core Utilization:**
```bash
# Scale workers with CPU affinity
docker compose -f docker-compose.prod.yml up -d --scale worker=4

# Monitor CPU usage
docker compose -f docker-compose.prod.yml exec worker top
```

### Database Connection Scaling

#### PostgreSQL Connection Pooling

**Environment Variables:**
```bash
# Increase connection pool size
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=30
```

#### Redis Connection Scaling

**Redis Configuration:**
```bash
# Redis connection pool
REDIS_POOL_SIZE=5
REDIS_MAX_CONNECTIONS=20
```

### Monitoring and Alerting

#### Service Health Monitoring

**Health Check Script:**
```bash
#!/bin/bash
# health-check.sh

# Check API instances
for i in {1..3}; do
    if ! curl -f http://localhost:800$i/health; then
        echo "API instance $i is down"
        exit 1
    fi
done

# Check worker instances
if ! docker compose -f docker-compose.prod.yml exec worker celery -A app.worker.celery_app inspect ping; then
    echo "Worker is down"
    exit 1
fi

echo "All services healthy"
```

#### Auto-Scaling Triggers

**CPU-Based Scaling:**
```bash
# Monitor CPU usage and scale automatically
if [ $(docker stats --no-stream --format "table {{.CPUPerc}}" research_api_prod | tail -n +2 | sed 's/%//') -gt 80 ]; then
    docker compose -f docker-compose.prod.yml up -d --scale research-api=4
fi
```

**Queue-Based Scaling:**
```bash
# Scale workers based on queue length
QUEUE_LENGTH=$(docker compose -f docker-compose.prod.yml exec worker celery -A app.worker.celery_app inspect reserved | jq length)
if [ $QUEUE_LENGTH -gt 10 ]; then
    docker compose -f docker-compose.prod.yml up -d --scale worker=5
fi
```

### Best Practices

#### Zero-Downtime Deployment

1. **Rolling Updates**: Update one service at a time
2. **Health Checks**: Verify service health before proceeding
3. **Graceful Shutdown**: Allow running tasks to complete
4. **Load Balancing**: Distribute traffic across instances

#### Resource Planning

1. **Memory**: Plan for 2x current usage during scaling
2. **CPU**: Monitor utilization and scale accordingly
3. **Network**: Ensure sufficient bandwidth for load balancing
4. **Storage**: Monitor disk usage for logs and data

#### Monitoring Strategy

1. **Service Health**: Regular health checks
2. **Resource Usage**: CPU, memory, disk monitoring
3. **Queue Length**: Celery task queue monitoring
4. **Response Times**: API performance tracking

## Performance Optimization

### Backend Optimization

**Database Optimization:**
- Connection pooling
- Query optimization
- Indexing strategies
- Caching layers

**API Optimization:**
- Response compression
- Pagination for large datasets
- Async processing

### Frontend Optimization

**Bundle Optimization:**
- Code splitting
- Lazy loading
- Asset optimization

**User Experience:**
- Real-time updates
- Progressive loading
- Error boundaries
- Responsive design

## Error Handling

### Backend Error Handling

**Exception Management:**
- Global exception handlers
- Standard error responses
- Structured logging
- Graceful degradation

**Recovery Strategies:**
- Retry mechanisms
- Fallback responses
- State recovery

### Frontend Error Handling

**User Experience:**
- Error boundaries
- User-friendly messages
- Retry mechanisms

**Development Experience:**
- Error logging
- Debug information

## Testing Strategy

### Backend Testing

**Unit Testing:**
- Service layer testing
- Database operation testing
- API endpoint testing
- Mock implementations

**Integration Testing:**
- Database integration
- External API testing
- End-to-end workflows
- Performance testing

### Frontend Testing

**Component Testing:**
- React component testing
- Hook testing
- User interaction testing
- Accessibility testing

**E2E Testing:**
- User workflow testing
- Cross-browser testing
- Performance testing
- Visual regression testing

## Scalability Considerations

### Horizontal Scaling

**Backend Scaling:**
- Multiple FastAPI instances
- Celery worker scaling
- Database read replicas
- Load balancing

**Frontend Scaling:**
- Static asset optimization
- Caching strategies
- Progressive enhancement

### Vertical Scaling

**Resource Optimization:**
- Memory usage optimization
- CPU utilization
- Database performance
- Queue processing

**Capacity Planning:**
- Usage pattern analysis
- Resource requirement estimation
- Performance benchmarking
- Growth projection

## Maintenance and Operations

### Database Maintenance

**PostgreSQL:**
- Regular backups
- Index optimization
- Query performance tuning
- Connection management

**MongoDB:**
- Document cleanup
- Index maintenance
- Sharding considerations
- Backup strategies

### Application Maintenance

**Code Maintenance:**
- Dependency updates
- Security patches
- Performance optimization
- Feature enhancements

**Operational Maintenance:**
- Log rotation
- Disk space management
- Service monitoring
- Incident response

This technical documentation provides a comprehensive overview of the system architecture, implementation details, and operational considerations for the Product-Market Fit Research Assistant.
