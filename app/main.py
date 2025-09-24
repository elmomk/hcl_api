"""FastAPI application entrypoint for Terragrunt Automation API."""
from fastapi import FastAPI
from routers import config_creation

app = FastAPI()

app.include_router(config_creation.router)


@app.get("/")
async def read_root():
    """Health check endpoint to verify the API is running."""
    return {"Hello": "World"}


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Liveness probe: return 200 OK if the process is alive."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    """Readiness probe: return 200 OK when the app is ready to serve requests.

    In a minimal setup (no external deps), this mirrors liveness. Add checks here
    for DB connections, external services, or configuration as needed.
    """
    return {"status": "ready"}
