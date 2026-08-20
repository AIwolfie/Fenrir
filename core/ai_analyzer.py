"""AI Analysis core utilizing LLMs to synthesize OSINT data.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import os
from typing import Any
import requests

from config import (
    AI_MODEL,
    AI_PROVIDER,
    ANTHROPIC_API_KEY,
    GEMINI_API_KEY,
    OLLAMA_URL,
    OPENAI_API_KEY,
    OPENROUTER_API_KEY,
    USER_AGENT,
)
from utils.logger import get_logger

LOGGER = get_logger(__name__)


class AIAnalyzer:
    """Multi-provider LLM analysis engine for Dark Web threat triage."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self.provider = (provider or AI_PROVIDER).lower()
        self.model = model or AI_MODEL
        self.api_key = api_key
        self.endpoint_url = endpoint_url or OLLAMA_URL

    def generate_investigation_summary(
        self,
        target_url: str,
        text_content: str,
        metadata: dict[str, Any] | None = None,
        *,
        focus: str = "general",
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        endpoint_url: str | None = None,
    ) -> str:
        """Query LLM or fallback heuristics to generate an automated OSINT summary."""
        active_provider = (provider or self.provider or AI_PROVIDER).lower()
        active_model = model or self.model
        active_key = api_key or self.api_key
        active_endpoint = endpoint_url or self.endpoint_url

        metadata = metadata or {}
        if not text_content and not metadata:
            return "No content or metadata available for OSINT analysis."

        system_prompts = {
            "general": (
                "You are DeepRecon AI, an elite cybersecurity and threat intelligence expert "
                "analyzing Dark Web / Tor network intelligence. Summarize threat indicators, key services, "
                "identified infrastructure, operational security observations, and actionable leads concisely."
            ),
            "crypto_fraud": (
                "You are DeepRecon Financial Crime & Crypto Forensics AI. Thoroughly analyze "
                "cryptocurrency payment flows (BTC, ETH, XMR), suspected illicit trade, escrow services, "
                "and financial fraud indicators."
            ),
            "marketplace_drugs": (
                "You are DeepRecon Darknet Marketplace Analyst. Analyze vendor profiles, illicit contraband, "
                "counterfeits, credentials dumps, escrow mechanics, and operational security."
            ),
            "vulnerability_exploit": (
                "You are DeepRecon Offensive Security & Vulnerability Researcher. Analyze the underlying tech stack, "
                "server configurations, potential CVEs, login forms, exposed endpoints, and misconfigurations."
            ),
        }

        system_prompt = system_prompts.get(focus, system_prompts["general"])

        user_prompt = (
            f"Target URL: {target_url}\n"
            f"Extracted Metadata (Crypto/Emails/PGP/Tech): {metadata}\n\n"
            f"Page Content Snippet:\n{text_content[:4500]}\n\n"
            f"Provide a structured OSINT threat intelligence assessment in Clean Markdown covering:\n"
            f"### 1. Executive Summary & Purpose\n"
            f"### 2. Threat Classification (🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW) with Rationale\n"
            f"### 3. Identified Intelligence Artifacts (Crypto Wallets, Emails, PGP, Tech Stack)\n"
            f"### 4. OPSEC & Infrastructure Observations\n"
            f"### 5. Recommended Pivot Vectors & Actionable Leads"
        )

        try:
            if active_provider == "openai":
                return self._query_openai(system_prompt, user_prompt, model=active_model, api_key=active_key, endpoint=active_endpoint)
            elif active_provider == "anthropic":
                return self._query_anthropic(system_prompt, user_prompt, model=active_model, api_key=active_key)
            elif active_provider == "openrouter":
                return self._query_openrouter(system_prompt, user_prompt, model=active_model, api_key=active_key)
            elif active_provider == "gemini":
                return self._query_gemini(system_prompt, user_prompt, model=active_model, api_key=active_key)
            elif active_provider in ("ollama", "custom"):
                return self._query_ollama(system_prompt, user_prompt, model=active_model, endpoint=active_endpoint)
            else:
                return self._generate_heuristic_summary(target_url, text_content, metadata)
        except Exception as e:
            LOGGER.debug(f"AI Analyzer query error: {e}")
            return self._generate_heuristic_summary(target_url, text_content, metadata)

    def _query_ollama(self, system: str, user: str, model: str | None = None, endpoint: str | None = None) -> str:
        active_model = model or "llama3"
        url = endpoint or self.endpoint_url or "http://127.0.0.1:11434"
        
        # Check if OpenAI-compatible endpoint or native Ollama
        if "/v1" in url:
            resp = requests.post(
                f"{url.rstrip('/')}/chat/completions",
                json={
                    "model": active_model,
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                    "temperature": 0.3,
                },
                timeout=45,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            raise ConnectionError(f"Custom endpoint returned {resp.status_code}: {resp.text}")

        response = requests.post(
            f"{url.rstrip('/')}/api/generate",
            json={"model": active_model, "prompt": f"{system}\n\n{user}", "stream": False},
            timeout=45,
        )
        if response.status_code == 200:
            res_text = response.json().get("response", "").strip()
            if res_text:
                return res_text
        raise ConnectionError(f"Ollama returned status {response.status_code}")

    def _query_openai(
        self,
        system: str,
        user: str,
        model: str | None = None,
        api_key: str | None = None,
        endpoint: str | None = None,
    ) -> str:
        key = api_key or OPENAI_API_KEY
        if not key:
            raise ValueError("OpenAI API Key not configured.")
        active_model = model or "gpt-4o"
        url = endpoint or "https://api.openai.com/v1/chat/completions"
        if not url.endswith("/chat/completions"):
            url = f"{url.rstrip('/')}/chat/completions"

        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": active_model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "temperature": 0.3,
            },
            timeout=45,
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        raise RuntimeError(f"OpenAI API Error: {response.status_code} - {response.text}")

    def _query_anthropic(self, system: str, user: str, model: str | None = None, api_key: str | None = None) -> str:
        key = api_key or ANTHROPIC_API_KEY
        if not key:
            raise ValueError("Anthropic API Key not configured.")
        active_model = model or "claude-3-5-haiku-20241022"
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": active_model,
                "system": system,
                "messages": [{"role": "user", "content": user}],
                "max_tokens": 1500,
            },
            timeout=45,
        )
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        raise RuntimeError(f"Anthropic API Error: {response.status_code} - {response.text}")

    def _query_openrouter(self, system: str, user: str, model: str | None = None, api_key: str | None = None) -> str:
        key = api_key or OPENROUTER_API_KEY
        if not key:
            raise ValueError("OpenRouter API Key not configured.")
        active_model = model or "openai/gpt-4o-mini"
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": active_model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            },
            timeout=45,
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        raise RuntimeError(f"OpenRouter API Error: {response.status_code} - {response.text}")

    def _query_gemini(self, system: str, user: str, model: str | None = None, api_key: str | None = None) -> str:
        key = api_key or GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        if not key:
            raise ValueError("Gemini API Key not configured.")
        active_model = model or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={key}"
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": f"{system}\n\n{user}"}]}]},
            timeout=45,
        )
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        raise RuntimeError(f"Gemini API Error: {response.status_code} - {response.text}")

    def _generate_heuristic_summary(self, target_url: str, text_content: str, metadata: dict[str, Any]) -> str:
        """Deterministic OSINT heuristic triage summary when remote LLM is offline."""
        crypto = metadata.get("crypto", {}) or metadata.get("crypto_addresses", {})
        emails = metadata.get("emails", [])
        pgp = metadata.get("pgp", []) or metadata.get("pgp_blocks", [])
        tech = metadata.get("technologies", []) or metadata.get("detected_technologies", [])

        btc_count = len(crypto.get("bitcoin", []))
        eth_count = len(crypto.get("ethereum", []))
        xmr_count = len(crypto.get("monero", []))
        total_crypto = btc_count + eth_count + xmr_count

        risk_level = "LOW"
        if total_crypto > 0 or len(pgp) > 0:
            risk_level = "MEDIUM"
        if (btc_count > 2 or xmr_count > 0) and any(
            w in text_content.lower() for w in ["market", "escrow", "vendor", "leak", "dump", "carding"]
        ):
            risk_level = "HIGH"

        lines = [
            f"### 🛡️ DeepRecon OSINT Threat Summary (Automated Heuristic Triage)",
            f"",
            f"**Target Node:** `{target_url}`",
            f"**Risk Classification: {risk_level}**",
            f"",
            f"#### 💰 Cryptocurrency Artifacts ({total_crypto} total):",
            f"- **Bitcoin (BTC):** {btc_count} addresses ({', '.join(crypto.get('bitcoin', [])[:2]) if btc_count else 'None'})",
            f"- **Ethereum (ETH):** {eth_count} addresses ({', '.join(crypto.get('ethereum', [])[:2]) if eth_count else 'None'})",
            f"- **Monero (XMR):** {xmr_count} addresses ({', '.join(crypto.get('monero', [])[:2]) if xmr_count else 'None'})",
            f"",
            f"#### 📧 Extracted Contact Vectors:",
            f"- **Emails Discovered:** {len(emails)} ({', '.join(emails[:3]) if emails else 'None'})",
            f"- **PGP Public Keys:** {'Present (' + str(len(pgp)) + ' block)' if pgp else 'None'}",
            f"",
            f"#### 🛠️ Fingerprinted Technologies & Servers:",
            f"- `{', '.join(tech) if tech else 'Generic / Hidden Surface'}`",
            f"",
            f"#### 🚀 Recommended Actionable Leads:",
            f"1. Cross-reference discovered BTC/XMR addresses against known darknet market clusters.",
            f"2. Inspect login form endpoints for authentication bypass vectors.",
            f"3. Map internal links and sub-routes for exposed administrative dashboards.",
        ]
        return "\n".join(lines)