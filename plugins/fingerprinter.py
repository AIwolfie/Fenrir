"""Technology stack fingerprinter plugin for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import re
from typing import Any
from plugins import BasePlugin


class FingerprinterPlugin(BasePlugin):
    """
    Identifies technology stacks (Web servers, JS frameworks, Backend frameworks, CMS, CSS frameworks)
    from page HTML, response headers, script sources, and meta tags.
    """

    SIGNATURES = {
        # Backend Frameworks
        "FastAPI": [r"swagger-ui", r"/docs/openapi\.json", r"fastapi"],
        "Flask": [r"flask", r"werkzeug", r"session=ey"],
        "Django": [r"csrfmiddlewaretoken", r"__admin__", r"django"],
        "Express/Node": [r"x-powered-by:\s*express", r"connect\.sid", r"node_modules"],
        "PHP": [r"\.php", r"PHPSESSID", r"x-powered-by:\s*php"],
        "Ruby on Rails": [r"csrf-param.*authenticity_token", r"rails", r"_session_id"],
        "ASP.NET": [r"__VIEWSTATE", r"ASP\.NET_SessionId", r"\.aspx"],
        
        # Frontend Frameworks & Libraries
        "React": [r"data-reactroot", r"react-dom", r"_reactInternalInstance", r"__REACT_DEVTOOLS_GLOBAL_HOOK__"],
        "Next.js": [r"/_next/static", r"__NEXT_DATA__", r"next/head"],
        "Vue.js": [r"data-v-[a-f0-9]", r"vue\.runtime", r"__vue__"],
        "Nuxt.js": [r"/_nuxt/", r"__NUXT__"],
        "Angular": [r"ng-version", r"ng-app", r"ng-model", r"zone\.js"],
        "Svelte": [r"svelte-", r"__svelte"],
        "Alpine.js": [r"x-data", r"x-bind", r"alpine\.js"],
        "jQuery": [r"jquery[\.-][0-9\.]+", r"jquery\.min\.js"],

        # CMS & Applications
        "WordPress": [r"wp-content", r"wp-includes", r"generator[\"'\s]+content=[\"']WordPress"],
        "Joomla": [r"Joomla!", r"joomla\.xml", r"option=com_"],
        "Drupal": [r"Drupal\.settings", r"sites/all/modules", r"drupal\.js"],
        "Ghost": [r"ghost\.org", r"ghost-version"],
        "phpBB": [r"phpbb", r"viewtopic\.php"],

        # Web Servers & Edge
        "Nginx": [r"nginx", r"server:\s*nginx"],
        "Apache": [r"Apache", r"server:\s*Apache"],
        "Caddy": [r"server:\s*caddy", r"caddy"],
        "Lighttpd": [r"server:\s*lighttpd", r"lighttpd"],
        "Cloudflare": [r"cf-ray", r"cloudflare-nginx", r"cloudflare"],
        "OpenResty": [r"openresty", r"server:\s*openresty"],

        # CSS Frameworks
        "TailwindCSS": [r"tailwind", r"class=[\"'][^\"']*(?:flex|grid|hidden|text-center|bg-gray|p-[0-9])"],
        "Bootstrap": [r"bootstrap(?:\.min)?\.css", r"bootstrap(?:\.min)?\.js", r"class=[\"'][^\"']*(?:col-md-|btn-primary)"],
        "Bulma": [r"bulma(?:\.min)?\.css", r"class=[\"'][^\"']*(?:is-primary|navbar-menu)"],

        # Databases / APIs
        "GraphQL": [r"__schema", r"graphql", r"query\s*\{"],
        "MySQL": [r"SQL syntax.*MySQL", r"Warning.*mysql_"],
        "PostgreSQL": [r"PostgreSQL.*ERROR", r"pg_query"],
        "SQLite": [r"SQLite/JDBCDriver", r"sqlite3"],
    }

    @property
    def name(self) -> str:
        return "fingerprinter"

    @property
    def description(self) -> str:
        return "Identifies technology stack based on signatures in the HTML and headers."

    def extract(self, page: Any) -> dict[str, Any]:
        identified_tech = set()
        
        # Combine raw HTML and serialized headers for inspection
        headers_str = ""
        if hasattr(page, "headers") and isinstance(page.headers, dict):
            headers_str = " ".join(f"{k}: {v}" for k, v in page.headers.items())
        
        search_target = f"{getattr(page, 'raw_html', '') or ''} {getattr(page, 'text', '') or ''} {headers_str}"
        
        for tech, patterns in self.SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, search_target, re.IGNORECASE):
                    identified_tech.add(tech)
                    break

        return {"detected_technologies": sorted(identified_tech)}


PLUGIN_CLASS = FingerprinterPlugin
