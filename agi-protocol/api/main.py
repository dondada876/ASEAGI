"""
AGI Protocol FastAPI Backend
Port: 8000 (isolated from PROJ344 ports 8501-8506)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AGI Protocol API",
    description="Legal Defense Multi-Agent System API",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS middleware (allows access from PROJ344 dashboards if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 AGI Protocol API starting...")
    logger.info(f"   Port: {os.getenv('API_PORT', 8000)}")
    logger.info(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Verify environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        logger.error("   Please check your .env file")
    else:
        logger.info("✅ All required environment variables present")

    logger.info("✅ AGI Protocol API ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 AGI Protocol API shutting down...")
    logger.info("✅ Shutdown complete")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """Root endpoint - API information"""
    return {
        "name": "AGI Protocol API",
        "version": "0.1.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    Used by Docker healthcheck and monitoring systems
    """
    try:
        # Check environment variables
        env_check = all([
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        ])

        return {
            "status": "healthy" if env_check else "degraded",
            "version": "0.1.0",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "environment": "ok" if env_check else "missing_vars",
                "api": "ok"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/status", tags=["Health"])
async def status() -> Dict[str, Any]:
    """
    Detailed system status
    """
    return {
        "api": {
            "status": "operational",
            "version": "0.1.0",
            "uptime": "tracked_in_production"
        },
        "integrations": {
            "proj344": "connected" if os.getenv('SUPABASE_URL') else "not_configured",
            "telegram": "configured" if os.getenv('TELEGRAM_BOT_TOKEN') else "not_configured",
            "claude_api": "configured" if os.getenv('ANTHROPIC_API_KEY') else "not_configured"
        },
        "features": {
            "telegram_bot": bool(os.getenv('ENABLE_TELEGRAM_BOT', False)),
            "document_upload": True,
            "legal_analysis": True,
            "motion_generation": False  # Coming in Phase 4
        },
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# PLACEHOLDER ROUTERS (to be implemented)
# ============================================================================

# These will be moved to separate router files in api/routers/

@app.get("/api/v1/info", tags=["Info"])
async def api_info() -> Dict[str, str]:
    """API version and information"""
    return {
        "api_version": "v1",
        "status": "in_development",
        "endpoints": {
            "telegram": "/telegram/*",
            "documents": "/documents/*",
            "analysis": "/analysis/*"
        },
        "note": "This is a skeleton implementation. Full endpoints coming soon."
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"Endpoint {request.url.path} does not exist",
            "available_docs": "/docs",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    logger.info(f"Starting AGI Protocol API on {host}:{port}")
    logger.info(f"Reload mode: {reload}")
    logger.info(f"Documentation: http://{host}:{port}/docs")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
