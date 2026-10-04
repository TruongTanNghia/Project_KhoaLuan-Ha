"""Logging setup shared by every script and module.

Each script calls :func:`setup_logging` once; library modules only call
``logging.getLogger(__name__)`` (via :func:`get_logger`) and never configure
handlers themselves.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
ROOT_LOGGER_NAME = "lung_nodule_unet"


def setup_logging(
    run_name: str,
    log_dir: str | Path | None = None,
    level: str | int = "INFO",
) -> Path | None:
    """Configure console (+ optional file) logging for one run.

    Args:
        run_name: Used in the log file name, e.g. ``"01_validate_raw_data"``.
        log_dir: Directory for ``<run_name>_<timestamp>.log``; ``None`` = console only.
        level: Logging level name or number.

    Returns:
        Path of the log file, or ``None`` when ``log_dir`` is ``None``.
    """
    root = logging.getLogger(ROOT_LOGGER_NAME)
    root.setLevel(level)
    root.propagate = False
    # Remove handlers from a previous call (e.g. notebooks re-running a cell).
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    log_file: Path | None = None
    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{run_name}_{timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    return log_file


def get_logger(name: str) -> logging.Logger:
    """Return a child of the project logger, e.g. ``lung_nodule_unet.src.data.xml_parser``."""
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")
