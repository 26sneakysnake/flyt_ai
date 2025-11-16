from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.api import router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="flyt.ai API",
    description="AI-powered flight briefing system",
    version="0.1.0"
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "0.1.0"
        }
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "flyt.ai API",
        "version": "0.1.0",
        "docs": "/docs"
    }
