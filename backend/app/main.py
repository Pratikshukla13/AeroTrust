"""AeroTrust Observatory FastAPI Application Entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.api.endpoints import router as api_router

app = FastAPI(
    title="AeroTrust API",
    description="Data-integrity observatory for aircraft: GNSS interference & solar radiation monitoring.",
    version="1.0.0",
)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "project": "AeroTrust",
        "status": "operational",
        "data_mode": settings.DATA_MODE,
        "synthetic_notice": (
            "Results on synthetic data demonstrate the method, not real-world accuracy."
            if settings.DATA_MODE == "SYNTHETIC"
            else "REAL_DATA"
        ),
        "synthetic_banner_required": settings.DATA_MODE == "SYNTHETIC",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "data_mode": settings.DATA_MODE,
    }

