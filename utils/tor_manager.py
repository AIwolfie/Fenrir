"""Tor session and circuit management helpers for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

try:
    from stem import Signal
    from stem.control import Controller
except ImportError:  # pragma: no cover - optional dependency
    Signal = None
    Controller = None

from config import (
    AUTO_RENEW_AFTER,
    REQUEST_TIMEOUT,
    TOR_CHECK_URL,
    TOR_CONTROL_COOKIE,
    TOR_CONTROL_PASSWORD,
    TOR_CONTROL_PORT,
    TOR_GEO_URL,
    TOR_PROXY,
    USER_AGENT,
)
from utils.logger import get_logger


LOGGER = get_logger(__name__)


@dataclass(slots=True)
class TorStatus:
    """Current Tor state snapshot."""

    control_port_available: bool
    current_ip: str | None = None
    country: str | None = None


class TorManager:
    """Manage Tor-backed requests sessions and circuit renewals."""

    def __init__(
        self,
        proxy_url: str = TOR_PROXY,
        control_port: int = TOR_CONTROL_PORT,
        control_password: str = TOR_CONTROL_PASSWORD,
        control_cookie: str = TOR_CONTROL_COOKIE,
        check_url: str = TOR_CHECK_URL,
        geo_url: str = TOR_GEO_URL,
        request_timeout: int = REQUEST_TIMEOUT,
        user_agent: str = USER_AGENT,
        auto_renew_after: int = AUTO_RENEW_AFTER,
    ) -> None:
        self.proxy_url = proxy_url
        self.control_port = control_port
        self.control_password = control_password
        self.control_cookie = control_cookie
        self.check_url = check_url
        self.geo_url = geo_url
        self.request_timeout = request_timeout
        self.user_agent = user_agent
        self.auto_renew_after = auto_renew_after
        self._requests_since_renewal = 0

    def get_session(self) -> requests.Session:
        """Build a requests session configured for Tor."""

        session = requests.Session()
        session.headers.update({"User-Agent": self.user_agent})
        session.proxies.update({"http": self.proxy_url, "https": self.proxy_url})
        return session

    def get_current_ip(self) -> str | None:
        """Return the current exit IP if available."""

        try:
            response = self.get_session().get(self.check_url, timeout=self.request_timeout)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                return payload.get("IP") or payload.get("ip")
        except Exception as exc:  # pragma: no cover - network dependent
            LOGGER.debug("Unable to query Tor IP: %s", exc)
        return None

    def get_exit_country(self) -> str | None:
        """Return the exit node country if a geolocation endpoint is configured."""

        if not self.geo_url:
            return None
        try:
            response = self.get_session().get(self.geo_url, timeout=self.request_timeout)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                return payload.get("country") or payload.get("country_name")
        except Exception as exc:  # pragma: no cover - network dependent
            LOGGER.debug("Unable to query Tor country: %s", exc)
        return None

    def renew_ip(self) -> bool:
        """Request a new Tor circuit, returning True on success."""

        if Controller is None:
            LOGGER.warning("stem is not installed; Tor circuit renewal is unavailable")
            return False

        try:
            with Controller.from_port(port=self.control_port) as controller:
                self._authenticate(controller)
                controller.signal(Signal.NEWNYM)
            self._requests_since_renewal = 0
            return True
        except Exception as exc:  # pragma: no cover - tor dependent
            LOGGER.warning("Unable to renew Tor circuit: %s", exc)
            return False

    def _authenticate(self, controller: Any) -> None:
        """Authenticate with Tor using cookie or password methods."""

        if self.control_cookie:
            controller.authenticate(password=self.control_password or None, cookie_path=self.control_cookie)
            return
        if self.control_password:
            controller.authenticate(password=self.control_password)
            return
        controller.authenticate()

    def record_request(self) -> bool:
        """Track requests and renew Tor after the configured threshold."""

        self._requests_since_renewal += 1
        if self.auto_renew_after > 0 and self._requests_since_renewal >= self.auto_renew_after:
            return self.renew_ip()
        return True

    def status(self) -> TorStatus:
        """Return a snapshot of the Tor state."""

        return TorStatus(
            control_port_available=Controller is not None,
            current_ip=self.get_current_ip(),
            country=self.get_exit_country(),
        )


_DEFAULT_MANAGER = TorManager()


def get_session() -> requests.Session:
    """Return a Tor-configured HTTP session for legacy callers."""

    return _DEFAULT_MANAGER.get_session()


def renew_ip() -> bool:
    """Renew the Tor circuit using the default manager."""

    return _DEFAULT_MANAGER.renew_ip()
