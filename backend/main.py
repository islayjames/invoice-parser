"""
Invoice Parser Backend API
FastAPI application for AI-powered invoice parsing using GPT-4o
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logger import configure_logging, get_logger
import os

# Configure structured logging
log_level = os.getenv("LOG_LEVEL", "INFO")
configure_logging(log_level)

logger = get_logger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Invoice Parser API",
    description="AI-powered invoice parsing using GPT-4o Vision API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "invoice-parser-api",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Invoice Parser API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Invoice Parser API starting up...")
    logger.info("Environment: development")
    logger.info("CORS origins configured")


# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Invoice Parser API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
