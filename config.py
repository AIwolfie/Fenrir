"""Fenrir configuration management.

Author: AIwolfie
Repository: https://github.com/AIwolfie/Fenrir

Values can be overridden with environment variables or a local .env file.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
	from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
	load_dotenv = None


if load_dotenv is not None:
	load_dotenv()


def _get_str(name: str, default: str) -> str:
	value = os.getenv(name)
	return value if value else default


def _get_int(name: str, default: int) -> int:
	value = os.getenv(name)
	return int(value) if value else default


def _get_float(name: str, default: float) -> float:
	value = os.getenv(name)
	return float(value) if value else default


def _get_bool(name: str, default: bool) -> bool:
	value = os.getenv(name)
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_list(name: str, default: list[str]) -> list[str]:
	value = os.getenv(name)
	if not value:
		return default
	return [item.strip() for item in value.split(",") if item.strip()]


TOR_PROXY = _get_str("TOR_PROXY", "socks5h://127.0.0.1:9050")
TOR_CONTROL_PORT = _get_int("TOR_CONTROL_PORT", 9051)
TOR_CONTROL_PASSWORD = _get_str("TOR_CONTROL_PASSWORD", "")
TOR_CONTROL_COOKIE = _get_str("TOR_CONTROL_COOKIE", "")
TOR_CHECK_URL = _get_str("TOR_CHECK_URL", "https://check.torproject.org/api/ip")
TOR_GEO_URL = _get_str("TOR_GEO_URL", "")

CRAWL_DEPTH = _get_int("CRAWL_DEPTH", 2)
CRAWL_WORKERS = _get_int("CRAWL_WORKERS", 5)
CRAWL_DELAY = _get_float("CRAWL_DELAY", 1.5)
REQUEST_TIMEOUT = _get_int("REQUEST_TIMEOUT", 30)
MAX_RETRIES = _get_int("MAX_RETRIES", 3)
AUTO_RENEW_AFTER = _get_int("AUTO_RENEW_AFTER", 20)
BYPASS_ROBOTS = _get_bool("BYPASS_ROBOTS", False)

PLUGINS_ENABLED = _get_list(
	"PLUGINS_ENABLED",
	["email_extractor", "crypto_detector", "pgp_harvester", "language_detector", "fingerprinter"],
)

PROXY_LIST = _get_list("PROXY_LIST", [])

DB_PATH = _get_str("DB_PATH", "storage/fenrir.db")
REPORTS_PATH = _get_str("REPORTS_PATH", "storage/reports/")
USER_AGENT = _get_str(
	"USER_AGENT",
	"Mozilla/5.0 (compatible; Fenrir/OSINT; Research; by AIwolfie)",
)

ENABLE_PDF_EXPORT = _get_bool("ENABLE_PDF_EXPORT", False)
ENABLE_HEADER_LOGGING = _get_bool("ENABLE_HEADER_LOGGING", True)

AI_PROVIDER = _get_str("AI_PROVIDER", "ollama")  # ollama, openai, anthropic, openrouter, gemini
AI_MODEL = _get_str("AI_MODEL", "")
OPENAI_API_KEY = _get_str("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = _get_str("ANTHROPIC_API_KEY", "")
OPENROUTER_API_KEY = _get_str("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = _get_str("GEMINI_API_KEY", "")
OLLAMA_URL = _get_str("OLLAMA_URL", "http://127.0.0.1:11434")

BASE_DIR = Path(__file__).resolve().parent
