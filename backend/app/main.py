from fastapi import FastAPI

from app.api.routes import health
from app.core.config import settings
from app.api.routes import health, jobs

app = FastAPI(title=settings.app_name)
app.include_router(health.router)
app.include_router(jobs.router)