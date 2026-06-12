"""
logging_config.py — Structured logging setup.
Logs to both console (INFO+) and a rotating file (DEBUG+).
"""

import logging
import logging.handlers
import os

LOG_DIR  = "logs"
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")


def setup_logging(verbose: bool = False) -> None:
    """
    Call this once at application startup.

    Console  → INFO  (or DEBUG if verbose=True)
    File     → DEBUG always  (rotates at 5 MB, keeps 3 backups)
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    root = logging.getLogger("trading_bot")
    root.setLevel(logging.DEBUG)          # capture everything; handlers filter

    # ── Console handler ────────────────────────────────────────────────────
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(logging.Formatter(
        fmt="%(levelname)-8s %(message)s",
    ))

    # ── Rotating file handler ───────────────────────────────────────────────
    file_h = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,   # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_h.setLevel(logging.DEBUG)
    file_h.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    root.addHandler(console)
    root.addHandler(file_h)

    root.info("Logging initialised. Log file: %s", LOG_FILE)