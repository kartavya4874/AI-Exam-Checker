"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db

# Create FastAPI app
app = FastAPI(
    title="Exam Checker API",
    description="Automated exam evaluation system for universities",
    version="1.0.0",
    debug=settings.debug
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")
    print(f"✅ Backend running at {settings.backend_url}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Exam Checker API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "gemini_api": "configured" if settings.gemini_api_key else "not configured",
        "ocr_api": "configured" if settings.google_cloud_vision_api_key else "not configured"
    }


# Import and include routers
from .api.documents import router as documents_router
from .api.evaluation import router as evaluation_router
from .api.review import router as review_router
from .api.export import router as export_router

app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(evaluation_router, prefix="/api/evaluation", tags=["evaluation"])
app.include_router(review_router, prefix="/api/review", tags=["review"])
app.include_router(export_router, prefix="/api/export", tags=["export"])
# app.include_router(review.router, prefix="/api/review", tags=["review"])
