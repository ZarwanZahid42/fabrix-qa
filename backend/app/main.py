"""
FabriX-QA Backend — FastAPI Application Entry Point
====================================================
This module bootstraps the FastAPI application:
  - Registers all API routers (auth, grading, alerts, reports, websockets)
  - Configures CORS middleware for the Next.js frontend
  - Connects to PostgreSQL (SQLAlchemy) and MongoDB (Motor) on startup
  - Sets up JWT authentication middleware

TODO:
  - Wire up lifespan context manager for DB connections
  - Add Prometheus /metrics endpoint
  - Rate limiting with slowapi
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.api import auth, grading, alerts, reports  # uncomment as modules are built
# from app.websockets import defect_stream             # uncomment when WS module is ready

app = FastAPI(
    title="FabriX-QA API",
    description="AI-powered fabric defect detection and quality grading system.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with FRONTEND_URL from env in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check — returns service status."""
    return {"status": "ok", "service": "FabriX-QA API"}
