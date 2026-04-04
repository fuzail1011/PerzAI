from fastapi import FastAPI
from app.db.init_db import ensure_database, init_db_models
from api import auth as auth_router
from api import persona as persona_router
from api import ingest as ingest_router
from api import retrieve as retrieve_router
from api import ui as ui_router
from loguru import logger
from app.core.logger import setup_logger


def create_app() -> FastAPI:
    app = FastAPI(title="PerzAI API")
    setup_logger()

    @app.on_event("startup")
    async def startup():
        ensure_database()
        logger.info("🚀 FastAPI application started")
        await init_db_models()

    app.include_router(auth_router.router)
    app.include_router(persona_router.router)
    app.include_router(ingest_router.router)
    app.include_router(retrieve_router.router)
    app.include_router(ui_router.router)

    return app


app = create_app()
