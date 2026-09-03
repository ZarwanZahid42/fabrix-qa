"""Purpose: provide the minimal FastAPI application bootstrap for scaffold smoke tests."""

from fastapi import FastAPI

app = FastAPI(title="FabriX-QA API", version="0.1.0")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return the scaffold service health status."""
    return {"status": "ok", "service": "fabrix-qa-backend"}
