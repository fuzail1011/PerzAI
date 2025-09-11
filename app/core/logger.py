from loguru import logger
import sys
import os
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "perzAI.log"


def setup_logger():
    # Create log directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)

    logger.remove()  # Remove default handler

    # Log to stdout (console)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        level="DEBUG",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # Log to file with rotation and retention
    logger.add(
        LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG",
        rotation="10 MB",  # Rotate after 10MB
        retention="30 days",  # Keep logs for 7 days
        compression="zip",  # Compress rotated logs
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info("✅ Logger initialized and writing to log/perzAI.log")
