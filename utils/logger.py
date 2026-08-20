"""Rich-powered logging helpers for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import logging
import sys

try:
    from rich.logging import RichHandler
except ImportError:  # pragma: no cover - optional dependency
    RichHandler = None


def configure_logging(level: int | str = logging.INFO) -> None:
    """Configure the root logger for DeepRecon."""

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    if RichHandler is not None:
        handler: logging.Handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_path=False,
        )
    else:
        handler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )


def get_logger(name: str = "DeepRecon") -> logging.Logger:
    """Return a configured logger instance."""

    configure_logging()
    return logging.getLogger(name)


logger = get_logger("DeepRecon")
