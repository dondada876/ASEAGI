"""
ASEAGI FastAPI Application
===========================

Main FastAPI application for ASEAGI system.

This API provides access to ASEAGI case management data for:
- Telegram bot
- Mobile applications
- n8n automation workflows
- Third-party integrations

Architecture:
    Telegram/Apps → FastAPI → Shared Service Layer → Supabase
    Claude Desktop → MCP Servers → Shared Service Layer → Supabase

By using a shared service layer, we ensure consistent data access
and business logic across all communication channels.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime

# Import routers
from telegram_endpoints import router as telegram_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ASEAGI API",
    description="Case Management System API for In re Ashe B., J24-00478",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Middleware
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()

    # Log request
    logger.info(f"{request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response time
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")

    return response


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc),
            "path": request.url.path
        }
    )


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ASEAGI API",
        "version": "1.0.0",
        "description": "Case Management System API",
        "case": "In re Ashe B., J24-00478",
        "endpoints": {
            "telegram": "/telegram/*",
            "docs": "/docs",
            "health": "/health"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ASEAGI API",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "supabase_configured": bool(os.environ.get("SUPABASE_URL")),
            "telegram_configured": bool(os.environ.get("TELEGRAM_BOT_TOKEN"))
        }
    }


# ============================================================================
# Include Routers
# ============================================================================

# Telegram bot endpoints
app.include_router(telegram_router)

# Future routers can be added here:
# app.include_router(n8n_router)
# app.include_router(mobile_router)
# app.include_router(webhooks_router)


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 60)
    logger.info("ASEAGI API Starting...")
    logger.info("=" * 60)

    # Check required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    logger.info("✓ Environment variables validated")
    logger.info(f"✓ Supabase URL: {os.environ.get('SUPABASE_URL')}")
    logger.info(f"✓ Telegram configured: {bool(os.environ.get('TELEGRAM_BOT_TOKEN'))}")
    logger.info("=" * 60)
    logger.info("ASEAGI API Started Successfully")
    logger.info("For Ashe. For Justice. For All Children. 🛡️")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("ASEAGI API shutting down...")


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "8000"))
    reload = os.environ.get("API_RELOAD", "false").lower() == "true"

    logger.info(f"Starting Uvicorn server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
