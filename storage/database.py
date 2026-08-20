"""Backward-compatible import wrapper for the storage module."""

from storage.db import DeepReconDB, FenrirDB, init_db, save_result

__all__ = ["FenrirDB", "DeepReconDB", "init_db", "save_result"]
