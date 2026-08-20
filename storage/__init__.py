"""Storage package for DeepRecon."""

from storage.db import DeepReconDB, init_db, save_result
from storage.models import KeywordHit, Link, Page, Report, Session, Site

__all__ = [
    "DeepReconDB",
    "KeywordHit",
    "Link",
    "Page",
    "Report",
    "Session",
    "Site",
    "init_db",
    "save_result",
]
