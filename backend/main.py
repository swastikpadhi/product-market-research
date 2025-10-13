"""
Research Assistant API - Market research and competitive intelligence platform.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_logger, settings
from app.services.application_manager import application_manager
from app.routes.research_routes import router as research_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Initialize all services
    success = await application_manager.initialize_all_services()
    if not success:
        raise RuntimeError("Failed to initialize services")
    
    yield
    
    # Cleanup services
    await application_manager.cleanup_services()


# FastAPI application
app = FastAPI(
    title="Research Assistant API",
    description="AI-powered market research and competitive intelligence platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with dependency status."""
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "service": "research_assistant_api",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "dependencies": application_manager.get_health_status()
    }
    
    # Determine overall status based on dependencies
    dependencies = health_status["dependencies"]
    if any(status not in ["healthy", "configured"] for status in dependencies.values()):
        health_status["status"] = "degraded"
    
    return health_status


app.include_router(research_router, prefix="/api/v1/research", tags=["Research"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled error on {request.url.path} [{request.method}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.port,
        reload=True,
        log_config=None  # Use logging from config.py
    )
