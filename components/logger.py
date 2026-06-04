import logging
import logging.handlers
from pathlib import Path

def get_logger():
    logger = logging.getLogger("huskontroller")

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # prevent Kivy's logging config from double-printing

        log_dir = Path(__file__).resolve().parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Rotating file handler — 100 MB max, one backup
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "huskontroller.log",
            maxBytes=100 * 1024 * 1024,
            backupCount=2
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler — replaces ad-hoc print()s
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Format: "2026-06-03 14:03:11 [INFO] [switcher] Sent command '2!' (select_hdmi)"
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(source)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Filter supplies default source="system" so plain logger.info() calls work
        def source_filter(record):
            if not hasattr(record, "source"):
                record.source = "system"
            return True

        for handler in (file_handler, console_handler):
            handler.setFormatter(formatter)
            handler.addFilter(source_filter)
            logger.addHandler(handler)

    return logger