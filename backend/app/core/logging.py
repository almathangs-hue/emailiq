import sys
import logging
from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    # Remove default loguru handler
    logger.remove()

    # Console — structured, human-readable in dev
    logger.add(
        sys.stdout,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "{message}"
        ),
        colorize=True,
    )

    # File — JSON structured for prod log aggregation
    logger.add(
        "logs/emailiq.log",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        serialize=True,  # JSON output
    )

    # Intercept standard library logging (SQLAlchemy, uvicorn, etc.)
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            level = logger.level(record.levelname).name if record.levelname in logger._core.levels else record.levelno
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
