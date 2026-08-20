"""Plugin system for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from typing import Any, Iterable

from core.parser import PageData


@dataclass(slots=True)
class PluginResult:
    """Standard plugin output container."""

    plugin: str
    results: dict[str, Any]


class BasePlugin:
    """Base class for DeepRecon plugins."""

    name = "base"

    def extract(self, page: PageData) -> dict[str, Any]:
        """Extract data from a parsed page."""

        raise NotImplementedError


def discover_plugins(enabled: Iterable[str] | None = None) -> list[BasePlugin]:
    """Discover and instantiate enabled plugins from this package."""

    enabled_set = {item.strip() for item in enabled or []}
    discovered: list[BasePlugin] = []
    package_name = __name__
    for module_info in pkgutil.iter_modules(__path__):
        if module_info.name in {"__init__", "base"}:
            continue
        if enabled_set and module_info.name not in enabled_set:
            continue
        module = importlib.import_module(f"{package_name}.{module_info.name}")
        plugin_class = getattr(module, "PLUGIN_CLASS", None)
        if plugin_class is not None:
            discovered.append(plugin_class())
    return discovered
