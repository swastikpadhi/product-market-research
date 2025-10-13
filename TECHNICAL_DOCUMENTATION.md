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

**API Gateway Layer:**
- **Nginx Reverse Proxy** - Static file serving and API routing
- **SSL/TLS Termination** - Secure communication
- **Load Balancing** - Request distribution

**Backend Services Layer:**
- **FastAPI Application** - RESTful API with async support
- **Celery Task Queue** - Background job processing
- **LangGraph Supervisor** - Multi-agent orchestration
- **Credit Management** - Usage tracking and billing

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

**Frontend:**
- React SPA with real-time updates
- Tailwind CSS for styling
- Custom hooks for state management
- Export functionality for detailed report sharing

**Databases:**
- PostgreSQL: Structured data (credit transactions)
- MongoDB: Unstructured research results
- Redis: Caching and task queue broker

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

### Progress Tracking

**Checkpoint System:**
- 17 predefined checkpoints
- Real-time progress updates
- Status persistence in Redis
- Frontend polling for updates

**Checkpoint Categories:**
- Initialization (1 checkpoint)
- Query Generation (1 checkpoint)
- Market Research (4 checkpoints)
- Competitor Research (4 checkpoints)
- Customer Research (4 checkpoints)
- Report Generation (2 checkpoints)
- Final Delivery (1 checkpoint)

## Credit System

### Credit Management

**Credit Allocation:**
- Monthly credit limits per user
- Usage tracking and enforcement
- Transaction logging for audit
- Balance updates with atomic operations

**Credit Costs:**
- Essential Research: 6 credits
- Standard Research: 12 credits
- Deep Research: 18 credits

**Credit Operations:**
- Account creation with initial balance
- Credit deduction on research submission
- Monthly reset and limit enforcement
- Transaction history and reporting

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

## Security Considerations

### API Security

**Authentication:**
- API key validation
- Rate limiting
- Request sanitization
- CORS configuration

**Data Protection:**
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Secure environment variable handling

### Infrastructure Security

**Network Security:**
- VPC configuration
- Security group rules
- SSL/TLS encryption
- Database access controls

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
