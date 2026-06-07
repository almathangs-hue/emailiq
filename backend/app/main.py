from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import EXCEPTION_HANDLERS
from app.api.v1.router import api_router


def _run_scheduled_sync():
    """Background job: auto-sync all connected accounts."""
    from app.db.session import SessionLocal
    from app.repositories.account import AccountRepository
    from app.services.sync_service import SyncService
    from datetime import date, timedelta

    db = SessionLocal()
    try:
        accounts = db.query(__import__("app.models.account", fromlist=["ConnectedAccount"]).ConnectedAccount).all()
        for account in accounts:
            try:
                service = SyncService(db)
                end = date.today()
                start = end - timedelta(days=1)
                service.sync_account(account.user_id, start, end)
            except Exception as exc:
                logger.error("Scheduled sync failed", account_id=account.id, error=str(exc))
    finally:
        db.close()


scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("EmailIQ API starting up")
    scheduler.add_job(
        _run_scheduled_sync,
        "interval",
        hours=settings.sync_interval_hours,
        id="auto_sync",
    )
    scheduler.start()
    yield
    scheduler.shutdown()
    logger.info("EmailIQ API shut down")


app = FastAPI(
    title="EmailIQ API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Register domain exception handlers
for exc_class, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exc_class, handler)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": "1.0.0"}
