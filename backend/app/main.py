"""
PharmaLens Backend - Main Application

FastAPI application entry point with all routes and middleware configured.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import health, prescriptions, search, auth, agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown operations.
    """
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📍 Environment: {settings.app_env}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🤖 LangChain Agent enabled")
    
    yield
    
    # Shutdown
    print(f"👋 Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🔬 **PharmaLens API** - AI-Powered Prescription Scanner & Medicine Price Comparison
    
    Upload prescription images, extract medicine names using OCR and AI, 
    and compare prices across Indian pharmacies to find the best deals.
    
    ## Features
    - 📸 Prescription image upload via Cloudinary
    - 🔍 OCR text extraction using Google Cloud Vision
    - 💊 AI-powered medicine name extraction using OpenAI GPT
    - 💰 Price comparison across 1mg, PharmEasy, Netmeds
    - 📊 Search history and savings tracking
    - 🤖 LangChain AI Agent for natural language queries
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(prescriptions.router, prefix="/api/prescriptions", tags=["Prescriptions"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(agent.router, prefix="/api/agent", tags=["AI Agent"])

# Multi-Agent System (CrewAI)
from app.api.routes import crew
app.include_router(crew.router, prefix="/api/crew", tags=["AI Crew"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to docs."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health"
    }
