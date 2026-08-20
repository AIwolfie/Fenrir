"""FastAPI Web UI and REST API server for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any

import requests
import uvicorn
from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import (
    AI_MODEL,
    AI_PROVIDER,
    CRAWL_DELAY,
    CRAWL_DEPTH,
    CRAWL_WORKERS,
    DB_PATH,
    MAX_RETRIES,
    OLLAMA_URL,
    REPORTS_PATH,
    REQUEST_TIMEOUT,
    TOR_PROXY,
)
from core.ai_analyzer import AIAnalyzer
from core.crawler import AsyncCrawler
from core.reporter import ReportGenerator
from core.search_engines import AsyncMetaSearch
from storage.db import FenrirDB
from utils.logger import get_logger
from utils.tor_manager import TorManager, renew_ip
from utils.validator import is_onion_url, sanitize_url

LOGGER = get_logger(__name__)

app = FastAPI(
    title="Fenrir Cyber Command Center • AIwolfie",
    description="Autonomous Dark Web Reconnaissance, AI Threat Triage & SOCKS5 Intelligence Platform by AIwolfie",
    version="3.2.0",
)

template_dir = Path(__file__).resolve().parent / "templates"
template_dir.mkdir(parents=True, exist_ok=True)

reports_dir = Path(REPORTS_PATH)
reports_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(template_dir))
db = FenrirDB(DB_PATH)
tor_manager = TorManager()
ai_analyzer = AIAnalyzer()

ACTIVE_CRAWLERS: dict[int, AsyncCrawler] = {}


def _crawl_background_job(
    seed_urls: list[str],
    session_id: int,
    depth: int = CRAWL_DEPTH,
    workers: int = CRAWL_WORKERS,
    delay: float = CRAWL_DELAY,
) -> None:
    """Execute background crawl with configured crawler parameters."""
    crawler = AsyncCrawler(
        db=db,
        session_id=session_id,
        depth=depth,
        workers=workers,
        delay=delay,
        timeout=REQUEST_TIMEOUT,
        proxy_url=TOR_PROXY,
        max_retries=MAX_RETRIES,
    )
    ACTIVE_CRAWLERS[session_id] = crawler
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(crawler.crawl(seed_urls))
        final_status = "stopped" if crawler._stop_requested else "completed"
        LOGGER.info("Crawl finished for session %d (%s): %d pages found", session_id, final_status, len(results))
        with db._connect() as conn:
            conn.execute("UPDATE sessions SET status = ? WHERE id = ?", (final_status, session_id))
    except Exception as exc:
        LOGGER.error("Crawl error in background job: %s", exc)
        with db._connect() as conn:
            conn.execute("UPDATE sessions SET status = 'failed' WHERE id = ?", (session_id,))
    finally:
        ACTIVE_CRAWLERS.pop(session_id, None)
        loop.close()


@app.get("/", response_class=HTMLResponse)
async def index_view(request: Request):
    """Render the primary single-page Cyber Command Center."""
    tor_ip = tor_manager.get_current_ip() or "Offline / Proxy Unreachable"
    sessions = db.list_sessions()
    total_pages = db.count_rows("pages")
    total_links = db.count_rows("links")
    total_keywords = db.count_rows("keywords_found")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tor_ip": tor_ip,
            "ai_provider": AI_PROVIDER.upper(),
            "ai_model": AI_MODEL or "default",
            "sessions": sessions,
            "total_pages": total_pages,
            "total_links": total_links,
            "total_keywords": total_keywords,
        },
    )


@app.get("/search", response_class=HTMLResponse)
async def search_redirect(request: Request, q: str = ""):
    """Search route compatible with standard queries or redirects."""
    return await index_view(request)


# ---------------------------------------------------------------------------
# REST API Endpoints for Reactive UI
# ---------------------------------------------------------------------------

@app.get("/api/status")
async def api_status():
    """Return live system telemetry and OPSEC health."""
    current_ip = tor_manager.get_current_ip() or "Offline / Proxy Unreachable"
    return JSONResponse(
        {
            "status": "online",
            "tor": {
                "exit_ip": current_ip,
                "is_active": "Offline" not in current_ip,
                "proxy": TOR_PROXY,
            },
            "ai": {
                "provider": AI_PROVIDER.upper(),
                "model": AI_MODEL or "default",
            },
            "metrics": {
                "total_pages": db.count_rows("pages"),
                "total_links": db.count_rows("links"),
                "total_keywords": db.count_rows("keywords_found"),
                "total_sessions": len(db.list_sessions()),
            },
        }
    )


@app.get("/api/sessions")
async def api_get_sessions():
    """Return all recorded reconnaissance sessions with aggregated counts."""
    sessions = db.list_sessions()
    enriched = []
    for s in sessions:
        pages = db.list_pages(s["id"])
        enriched.append(
            {
                "id": s["id"],
                "name": s["name"],
                "seed_url": s.get("seed_url") or "",
                "status": s.get("status") or "active",
                "started_at": s.get("started_at") or "",
                "page_count": len(pages),
            }
        )
    return JSONResponse({"sessions": enriched})


@app.get("/api/sessions/{session_id}")
async def api_get_session_details(session_id: int):
    """Return complete forensic data for a specific session."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    pages = db.list_pages(session_id)
    keyword_hits = db.list_keyword_hits(session_id)

    crypto_hits: dict[str, list[str]] = {"bitcoin": [], "ethereum": [], "monero": []}
    emails_set: set[str] = set()
    pgp_set: set[str] = set()
    tech_set: set[str] = set()

    for p in pages:
        meta = p.get("meta") or {}
        crypto = meta.get("crypto") or meta.get("crypto_addresses") or {}
        crypto_hits["bitcoin"].extend(crypto.get("bitcoin", []))
        crypto_hits["ethereum"].extend(crypto.get("ethereum", []))
        crypto_hits["monero"].extend(crypto.get("monero", []))

        for email in meta.get("emails", []):
            emails_set.add(email)
        for pgp in meta.get("pgp_blocks", []):
            pgp_set.add(pgp)
        for tech in meta.get("technologies", []):
            tech_set.add(tech)

    crypto_hits["bitcoin"] = sorted(list(set(crypto_hits["bitcoin"])))
    crypto_hits["ethereum"] = sorted(list(set(crypto_hits["ethereum"])))
    crypto_hits["monero"] = sorted(list(set(crypto_hits["monero"])))

    return JSONResponse(
        {
            "session": session,
            "pages": pages,
            "keyword_hits": keyword_hits,
            "crypto_hits": crypto_hits,
            "emails": sorted(list(emails_set)),
            "pgp_blocks": sorted(list(pgp_set)),
            "technologies": sorted(list(tech_set)),
        }
    )


@app.delete("/api/sessions/{session_id}")
async def api_delete_session(session_id: int):
    """Delete a reconnaissance session."""
    db.delete_session(session_id)
    return JSONResponse({"success": True, "message": f"Session #{session_id} deleted."})


@app.post("/api/scan")
async def api_start_scan(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    session_name: str = Form(None),
    depth: int = Form(CRAWL_DEPTH),
    workers: int = Form(CRAWL_WORKERS),
    delay: float = Form(CRAWL_DELAY),
):
    """Initiate an asynchronous reconnaissance crawl."""
    target_url = sanitize_url(url.strip())
    if not target_url:
        raise HTTPException(status_code=400, detail="Invalid target URL")

    if not session_name or not session_name.strip():
        session_name = f"OP_RECON_{int(time.time())}"
    else:
        session_name = session_name.strip()

    try:
        session_id = db.create_session(session_name, seed_url=target_url)
    except Exception:
        session_name = f"{session_name}_{int(time.time())}"
        session_id = db.create_session(session_name, seed_url=target_url)

    background_tasks.add_task(
        _crawl_background_job,
        [target_url],
        session_id,
        depth=max(1, depth),
        workers=max(1, min(workers, 20)),
        delay=max(0.0, delay),
    )

    return JSONResponse(
        {
            "success": True,
            "session_id": session_id,
            "session_name": session_name,
            "target_url": target_url,
            "message": f"Async reconnaissance swarm dispatched for {target_url}",
        }
    )


@app.post("/api/scan/{session_id}/stop")
async def api_stop_scan(session_id: int):
    """Abort an active reconnaissance crawl swarm."""
    crawler = ACTIVE_CRAWLERS.get(session_id)
    if crawler:
        crawler.stop()
        with db._connect() as conn:
            conn.execute("UPDATE sessions SET status = 'stopped' WHERE id = ?", (session_id,))
        return JSONResponse({"success": True, "message": f"Recon swarm for session #{session_id} abort signal sent."})

    with db._connect() as conn:
        conn.execute("UPDATE sessions SET status = 'stopped' WHERE id = ?", (session_id,))
    return JSONResponse({"success": True, "message": f"Session #{session_id} marked as stopped."})


@app.post("/api/scan/stop")
async def api_stop_all_scans():
    """Abort all currently running crawl swarms."""
    count = len(ACTIVE_CRAWLERS)
    for sid, crawler in list(ACTIVE_CRAWLERS.items()):
        crawler.stop()
        with db._connect() as conn:
            conn.execute("UPDATE sessions SET status = 'stopped' WHERE id = ?", (sid,))
    return JSONResponse({"success": True, "stopped_count": count, "message": f"Aborted {count} active crawl(s)."})


@app.post("/api/metasearch")
async def api_metasearch(query: str = Form(...)):
    """Query 11+ Dark Web search indexes concurrently."""
    clean_query = query.strip()
    if not clean_query:
        return JSONResponse({"query": "", "count": 0, "results": []})

    meta = AsyncMetaSearch()
    results = await meta.search(clean_query)
    return JSONResponse(
        {
            "query": clean_query,
            "count": len(results),
            "results": results,
        }
    )


@app.post("/api/ai_analyze")
async def api_ai_analyze(
    session_id: int = Form(None),
    target_url: str = Form(""),
    content: str = Form(""),
    provider: str = Form(None),
    model: str = Form(None),
    api_key: str = Form(None),
    endpoint_url: str = Form(None),
    focus: str = Form("general"),
):
    """Run an on-demand AI threat intelligence assessment with custom model and endpoint."""
    metadata: dict[str, Any] = {}
    url = target_url

    if session_id is not None:
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        pages = db.list_pages(session_id)
        if not pages:
            raise HTTPException(status_code=400, detail="No crawled pages in this session to analyze")
        target_page = pages[0]
        url = target_page["url"]
        content = target_page.get("content", "")
        metadata = target_page.get("meta", {})

    if not content and not url:
        raise HTTPException(status_code=400, detail="Provide either session_id or url + content")

    analyzer = AIAnalyzer(
        provider=provider,
        model=model,
        api_key=api_key,
        endpoint_url=endpoint_url,
    )
    summary = analyzer.generate_investigation_summary(
        target_url=url,
        text_content=content,
        metadata=metadata,
        focus=focus,
        provider=provider,
        model=model,
        api_key=api_key,
        endpoint_url=endpoint_url,
    )

    return JSONResponse(
        {
            "target_url": url,
            "provider": (provider or AI_PROVIDER).upper(),
            "model": model or AI_MODEL or "default",
            "summary": summary,
        }
    )


@app.get("/api/ai/models")
async def api_ai_models(endpoint_url: str = Query(None)):
    """Fetch locally available models from Ollama or OpenAI-compatible endpoint."""
    target_url = endpoint_url or OLLAMA_URL or "http://127.0.0.1:11434"
    try:
        if "/v1" in target_url:
            resp = requests.get(f"{target_url.rstrip('/')}/models", timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                return JSONResponse({"models": models})
        else:
            resp = requests.get(f"{target_url.rstrip('/')}/api/tags", timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                return JSONResponse({"models": models})
    except Exception as exc:
        LOGGER.debug("Could not fetch models: %s", exc)

    return JSONResponse(
        {
            "models": [
                "llama3",
                "llama3.1:8b",
                "llama3.1:70b",
                "mistral",
                "deepseek-r1",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash",
                "gpt-4o",
                "gpt-4o-mini",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
            ]
        }
    )


@app.get("/api/search")
async def api_search(q: str = Query(..., min_length=1), limit: int = Query(25, le=100)):
    """Search SQLite FTS5 BM25 indexed pages."""
    results = db.search_pages(q, limit=limit)
    return JSONResponse({"query": q, "count": len(results), "results": results})


@app.post("/api/report/generate")
async def api_generate_report(session_id: int = Form(...), title: str = Form(None)):
    """Generate a forensic intelligence report dossier (HTML/JSON/PDF)."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    generator = ReportGenerator(db=db, reports_path=reports_dir)
    report_title = title or session.get("name") or f"Session_{session_id}"
    outputs = generator.generate_session_report(session_id, title=report_title)

    html_name = outputs["html"].name
    json_name = outputs["json"].name
    pdf_name = outputs.get("pdf").name if "pdf" in outputs else None

    return JSONResponse(
        {
            "success": True,
            "session_id": session_id,
            "title": report_title,
            "files": {
                "html": f"/reports/{html_name}",
                "json": f"/reports/{json_name}",
                "pdf": f"/reports/{pdf_name}" if pdf_name else None,
            },
        }
    )


@app.get("/reports/{filename}")
async def api_get_report_file(filename: str):
    """Serve or download generated report artifacts."""
    file_path = reports_dir / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Report file not found")

    if filename.endswith(".html"):
        return FileResponse(file_path, media_type="text/html")
    elif filename.endswith(".json"):
        return FileResponse(file_path, media_type="application/json")
    elif filename.endswith(".pdf"):
        return FileResponse(file_path, media_type="application/pdf")
    return FileResponse(file_path)


@app.post("/api/tor/renew")
async def api_tor_renew():
    """Request a new Tor exit node circuit (NEWNYM)."""
    success = renew_ip()
    time.sleep(0.5)
    new_ip = tor_manager.get_current_ip() or "Rotated / Active"
    return JSONResponse(
        {
            "success": success,
            "tor_ip": new_ip,
            "message": "Tor identity renewed successfully" if success else "Tor control port unavailable",
        }
    )


def start_web_ui(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Launch the Web Command Center."""
    uvicorn.run("web.app:app", host=host, port=port, reload=False)
