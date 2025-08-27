import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Parse DATABASE_URL into components
    parsed_url = urlparse(DATABASE_URL)
    DB_USER: str = parsed_url.username or "postgres"
    DB_PASSWORD: str = parsed_url.password or "postgres"
    DB_HOST: str = parsed_url.hostname or "localhost"
    DB_PORT: str = str(parsed_url.port or 5432)
    DB_NAME: str = parsed_url.path.lstrip("/") or "postgres"

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # App
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", 8001))

    @classmethod
    def validate(cls) -> None:
        """Ensure required values are present."""
        missing = []
        if not cls.DATABASE_URL:
            missing.append("DATABASE_URL")
        if not cls.JWT_SECRET:
            missing.append("JWT_SECRET")
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
