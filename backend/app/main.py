"""
FastAPI application for Incentive Query UI

This is the main entry point for the backend API. It initializes the FastAPI app,
loads ML models as singletons during startup, and configures middleware.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.config import settings
from app.api import routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model storage (loaded once at startup)
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    CRITICAL: Models are loaded once at startup as singletons to avoid
    loading them on every request (which would be extremely slow).
    """
    logger.info("Starting up application...")
    
    # Load sentence transformer model for company search
    logger.info("Loading sentence transformer model...")
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    app_state['embedding_model'] = model
    logger.info(f"✓ Loaded embedding model: {settings.EMBEDDING_MODEL}")
    
    # Initialize Qdrant client (local file storage)
    logger.info("Initializing Qdrant client...")
    from qdrant_client import QdrantClient
    import os
    
    # Use local file storage like the rest of the project
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qdrant_path = os.path.join(project_root, "..", "qdrant_storage")
    
    qdrant_client = QdrantClient(path=qdrant_path)
    app_state['qdrant_client'] = qdrant_client
    logger.info(f"✓ Connected to Qdrant at {qdrant_path}")
    
    logger.info("Application startup complete!")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down application...")
    app_state.clear()


# Create FastAPI app
app = FastAPI(
    title="Incentive Query API",
    description="API for querying Portuguese public incentives and companies",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timeout middleware
class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request timeout"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(
                call_next(request),
                timeout=settings.API_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"Request timeout: {request.url}")
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "error": "Request Timeout",
                    "detail": f"Request exceeded {settings.API_TIMEOUT} seconds",
                    "status_code": 504
                }
            )


app.add_middleware(TimeoutMiddleware)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "status_code": 422
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "status_code": 500
        }
    )


# Include API routes
app.include_router(routes.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Incentive Query API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns service health status and component availability.
    """
    import psycopg2
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Check models loaded
    models_loaded = "embedding_model" in app_state and "qdrant_client" in app_state
    health_status["components"]["models"] = {
        "status": "healthy" if models_loaded else "unhealthy",
        "embedding_model_loaded": "embedding_model" in app_state,
        "qdrant_client_loaded": "qdrant_client" in app_state
    }
    
    # Check database connection
    try:
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            connect_timeout=5
        )
        conn.close()
        health_status["components"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Qdrant connection (if client is loaded)
    if "qdrant_client" in app_state:
        try:
            qdrant_client = app_state["qdrant_client"]
            collections = qdrant_client.get_collections()
            health_status["components"]["qdrant"] = {
                "status": "healthy",
                "collections": len(collections.collections)
            }
        except Exception as e:
            health_status["components"]["qdrant"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    return health_status


def get_app_state():
    """Get application state (models, clients, etc.)"""
    return app_state
