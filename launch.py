import uvicorn
from app.main import create_app
from app.config import Settings
from app.db.init_db import ensure_database, init_db_models

# validate configuration before starting server
Settings.validate()


async def startup():
    # Ensure DB exists before creating tables
    ensure_database()
    await init_db_models()


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "launch:app",
        host=Settings.APP_HOST,
        port=Settings.APP_PORT,
        reload=True,
    )
