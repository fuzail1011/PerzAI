from fastapi import FastAPI
from app.db.init_db import ensure_database, init_db_models
from api import auth as auth_router
from loguru import logger


def create_app() -> FastAPI:
    app = FastAPI(title="PerzAI API")

    @app.on_event("startup")
    async def startup():
        ensure_database()
        logger.info("🚀 FastAPI application started")
        await init_db_models()

    app.include_router(auth_router.router)

    @app.get("/")
    def root():
        return {"message": "🚀 PerzAI API is running"}

    return app


app = create_app()
