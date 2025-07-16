"""
LinkedIn Automation API - Main Application Entry Point

This is the main file that starts the FastAPI server.
It brings together all the API endpoints and configurations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from linkedin_automation.api.endpoints import router
from linkedin_automation.utils.logger import setup_logger
import uvicorn
from datetime import datetime

# Initialize logger
logger = setup_logger()

# Create FastAPI application instance
app = FastAPI(
    title="LinkedIn Automation API",
    description="A stealth LinkedIn automation service for connecting and messaging",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI will be available at /docs
    redoc_url="/redoc"  # ReDoc will be available at /redoc
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Root endpoint for health check
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LinkedIn Automation API is running!",
        "status": "healthy",
        "docs": "/docs",
        "api_version": "v1",
        "endpoints": {
            "login": "POST /api/v1/login",
            "connect": "POST /api/v1/connect", 
            "check_connection": "POST /api/v1/check_connection",
            "close": "GET /api/v1/close",
            "session_info": "GET /api/v1/session_info",
            "health": "GET /api/v1/health"
        }
    }

# Add global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "error_type": "system_error",
            "timestamp": datetime.now().isoformat()
        }
    )

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("LinkedIn Automation API starting up...")
    logger.info("API Documentation available at: /docs")
    logger.info("API endpoints available at: /api/v1/")

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("LinkedIn Automation API shutting down...")
    
    # Clean up browser resources if any
    try:
        from linkedin_automation.core.browser_manager import browser_manager
        if browser_manager.is_browser_active():
            browser_manager.close_browser()
            logger.info("Browser session cleaned up on shutdown")
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )