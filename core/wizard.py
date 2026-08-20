"""Interactive Guided Reconnaissance Wizard for Fenrir.

Author: AIwolfie
Repository: https://github.com/AIwolfie/Fenrir

Provides a frictionless, step-by-step interactive prompt flow that eliminates
the need for manual command-line flags and tags.
"""

from __future__ import annotations

import asyncio
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.theme import Theme

from config import (
    AI_MODEL,
    AI_PROVIDER,
    CRAWL_DELAY,
    CRAWL_DEPTH,
    CRAWL_WORKERS,
    DB_PATH,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    TOR_PROXY,
)
from core.ai_analyzer import AIAnalyzer
from core.crawler import AsyncCrawler
from core.reporter import ReportGenerator
from core.search_engines import AsyncMetaSearch
from core.searcher import Searcher
from storage.db import DeepReconDB
from utils.banner import banner
from utils.logger import get_logger
from utils.tor_manager import TorManager, renew_ip
from utils.validator import is_onion_url, sanitize_url

LOGGER = get_logger(__name__)

CUSTOM_THEME = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "danger": "bold red",
        "success": "bold green",
        "accent": "bold magenta",
        "dimmed": "dim white",
    }
)

console = Console(theme=CUSTOM_THEME)

CODENAME_ADJECTIVES = [
    "SHADOW", "CYBER", "PHANTOM", "GHOST", "VIPER", "HYDRA", "NEXUS",
    "DARK", "STEALTH", "SPECTRE", "COBALT", "OBSIDIAN", "AEGIS", "KRONOS"
]
CODENAME_NOUNS = [
    "RECON", "SPIDER", "PROTOCOL", "TRIAGE", "OPERATOR", "SENTINEL",
    "WATCHDOG", "HARVEST", "VECTOR", "CIRCUIT", "INFILTRATOR", "PROBE"
]


def generate_mission_codename() -> str:
    """Generate a cool tactical operation codename."""
    adj = random.choice(CODENAME_ADJECTIVES)
    noun = random.choice(CODENAME_NOUNS)
    tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    return f"OP_{adj}_{noun}_{tag}"


class ReconWizard:
    """Interactive guided intelligence wizard."""

    def __init__(self, db: DeepReconDB | None = None) -> None:
        self.db = db or DeepReconDB(DB_PATH)
        self.tor_manager = TorManager()
        self.ai_analyzer = AIAnalyzer()

    def run(self) -> None:
        """Launch the main interactive wizard menu."""
        while True:
            console.clear()
            banner()
            self._display_status_card()

            console.print("\n[bold #00f5d4]╭──────────────────────────────────────────────────────────────────────────╮[/bold #00f5d4]")
            console.print("[bold #00f5d4]│[/bold #00f5d4]   [bold white]🐺 FENRIR // TACTICAL MISSION CONTROL[/bold white] [dim cyan]• AIwolfie Threat Ops[/dim cyan]               [bold #00f5d4]│[/bold #00f5d4]")
            console.print("[bold #00f5d4]╰──────────────────────────────────────────────────────────────────────────╯[/bold #00f5d4]")
            console.print("[dim]Select an intelligence operation mode to begin guided setup:[/dim]\n")

            console.print("  [bold #00f5d4][1][/bold #00f5d4] 🎯 [bold]Interactive Recon Mission[/bold] [dim](Guided Crawler with Stealth/Deep Presets)[/dim]")
            console.print("  [bold #00f5d4][2][/bold #00f5d4] 🧅 [bold]Dark Web Meta-Search Infiltration[/bold] [dim](Multi-Engine Onion Discovery)[/dim]")
            console.print("  [bold #00f5d4][3][/bold #00f5d4] 📦 [bold]Batch Multi-Target Recon[/bold] [dim](Concurrent Scan List Infiltration)[/dim]")
            console.print("  [bold #00f5d4][4][/bold #00f5d4] 🤖 [bold]AI Threat Intelligence Analysis[/bold] [dim](Multi-LLM Target Dossier Synthesis)[/dim]")
            console.print("  [bold #00f5d4][5][/bold #00f5d4] 🔍 [bold]SQLite FTS5 Local Search[/bold] [dim](Sub-millisecond BM25 Text & Artifacts Query)[/dim]")
            console.print("  [bold #00f5d4][6][/bold #00f5d4] 📊 [bold]Generate Forensic Dossier Report[/bold] [dim](Dark Cyberpunk HTML / JSON / PDF)[/dim]")
            console.print("  [bold #00f5d4][7][/bold #00f5d4] 🔄 [bold]Rotate Tor Identity (NEWNYM)[/bold] [dim](Request Fresh Tor Exit Relay)[/dim]")
            console.print("  [bold #00f5d4][8][/bold #00f5d4] 🌐 [bold]Launch Modern Web UI Dashboard[/bold] [dim](Open Reactive Browser Command Center)[/dim]")
            console.print("  [bold #00f5d4][9][/bold #00f5d4] 🚪 [bold red]Exit Mission Control[/bold red]\n")

            choice = Prompt.ask(
                "[bold green]Select Operation[/bold green]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
                default="1",
            )

            if choice == "1":
                self._guided_recon_mission()
            elif choice == "2":
                self._guided_metasearch_mission()
            elif choice == "3":
                self._guided_batch_recon()
            elif choice == "4":
                self._guided_ai_analysis()
            elif choice == "5":
                self._guided_search()
            elif choice == "6":
                self._guided_report_generation()
            elif choice == "7":
                self._rotate_tor_ip()
            elif choice == "8":
                self._launch_web_ui()
                break
            elif choice == "9":
                console.print("\n[bold cyan]Shutting down Fenrir OSINT Framework. Stay safe out there.[/bold cyan] 🐺")
                break

            if choice not in ("8", "9"):
                console.print("\n[dim]Press Enter to return to Mission Control...[/dim]")
                input()

    def _display_status_card(self) -> None:
        """Render live system & OPSEC status card."""
        current_ip = self.tor_manager.get_current_ip() or "Offline / Proxy Unreachable"
        ip_status = f"[green]● {current_ip} (Encrypted)[/green]" if "Offline" not in current_ip else "[yellow]● Proxy Unreachable[/yellow]"
        
        pages_count = self.db.count_rows("pages")
        links_count = self.db.count_rows("links")
        hits_count = self.db.count_rows("keywords_found")
        sessions_count = len(self.db.list_sessions())

        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan")
        table.add_column()
        table.add_column(style="bold cyan")
        table.add_column()

        table.add_row("🧅 Tor Circuit:", ip_status, "🤖 AI Provider:", f"[magenta]{AI_PROVIDER.upper()}[/magenta]")
        table.add_row("💾 Storage DB:", f"[dim]{DB_PATH}[/dim]", "📁 Sessions:", f"[bold white]{sessions_count}[/bold white]")
        table.add_row("📄 Indexed Nodes:", f"[bold cyan]{pages_count}[/bold cyan]", "🔗 Graph Links:", f"[bold teal]{links_count}[/bold teal]")

        console.print(
            Panel(
                table,
                title="🛡️ [bold]System & OPSEC Diagnostics[/bold]",
                border_style="cyan",
            )
        )

    def _guided_recon_mission(self) -> None:
        """Step-by-step interactive single-target recon wizard."""
        console.print("\n[bold cyan]═══ 🎯 INTERACTIVE RECON MISSION SETUP ═══[/bold cyan]\n")

        # Step 1: Target Definition
        url_input = Prompt.ask("[bold]Enter Target URL[/bold] (.onion or clearnet)").strip()
        if not url_input:
            console.print("[red]Target URL cannot be empty.[/red]")
            return
        
        url = sanitize_url(url_input)
        if is_onion_url(url):
            console.print("  [green]✓ Validated Tor Hidden Service (.onion)[/green]")
        else:
            console.print("  [yellow]⚠ Target is a Clearnet URL.[/yellow]")
            if not Confirm.ask("  Proceed with clearnet routing via Tor proxy?", default=True):
                return

        # Step 2: Mission Codename
        default_codename = generate_mission_codename()
        session_name = Prompt.ask("[bold]Session Codename[/bold]", default=default_codename)

        # Step 3: Recon Profile Selection
        console.print("\n[bold]Select Recon Profile:[/bold]")
        console.print("  [cyan][1][/cyan] ⚡ [bold]Stealth Recon[/bold]       [dim](Depth: 1, Workers: 2, Delay: 2.5s — Low footprint)[/dim]")
        console.print("  [cyan][2][/cyan] 🔍 [bold]Standard Intel[/bold]      [dim](Depth: 2, Workers: 5, Delay: 1.5s — Recommended)[/dim]")
        console.print("  [cyan][3][/cyan] 🚀 [bold]Deep Infiltration[/bold]   [dim](Depth: 3, Workers: 10, Delay: 0.5s — High velocity)[/dim]")
        console.print("  [cyan][4][/cyan] 🛠️ [bold]Custom Profile[/bold]      [dim](Manual tuning of depth, concurrency & delay)[/dim]")

        profile_choice = Prompt.ask("Profile", choices=["1", "2", "3", "4"], default="2")

        if profile_choice == "1":
            depth, workers, delay = 1, 2, 2.5
        elif profile_choice == "2":
            depth, workers, delay = 2, 5, 1.5
        elif profile_choice == "3":
            depth, workers, delay = 3, 10, 0.5
        else:
            depth = IntPrompt.ask("  Traversal Depth (1-5)", default=CRAWL_DEPTH)
            workers = IntPrompt.ask("  Concurrent Workers (1-20)", default=CRAWL_WORKERS)
            delay = float(Prompt.ask("  Request Delay in seconds (e.g. 1.0)", default=str(CRAWL_DELAY)))

        # Step 4: AI Analysis Automation
        auto_ai = Confirm.ask("\n[bold]Execute automated AI Threat Assessment upon completion?[/bold]", default=True)

        # Confirm & Dispatch
        console.print("\n[bold green]Ready to dispatch recon swarm:[/bold green]")
        console.print(f"  • Target: [cyan]{url}[/cyan]")
        console.print(f"  • Session: [white]{session_name}[/white]")
        console.print(f"  • Scope: [dim]Depth {depth} | Workers {workers} | Delay {delay}s[/dim]")
        console.print(f"  • AI Triage: [magenta]{'Enabled (' + AI_PROVIDER.upper() + ')' if auto_ai else 'Disabled'}[/magenta]")

        if not Confirm.ask("\n[bold cyan]Initiate Operation?[/bold cyan]", default=True):
            console.print("[yellow]Mission aborted by operator.[/yellow]")
            return

        session_id = self.db.create_session(session_name, seed_url=url)

        crawler = AsyncCrawler(
            db=self.db,
            depth=depth,
            workers=workers,
            delay=delay,
            timeout=REQUEST_TIMEOUT,
            proxy_url=TOR_PROXY,
            max_retries=MAX_RETRIES,
        )

        console.print("\n[bold cyan]🚀 SOCKS5 Crawler Swarm Deployed...[/bold cyan]")
        with console.status("[bold green]Harvesting dark web nodes & extracting artifacts...[/bold green]", spinner="dots"):
            asyncio.run(crawler.crawl([url]))

        console.print(f"\n[bold green]✓ Reconnaissance mission completed for session #{session_id}![/bold green]")

        # Post-Crawl Artifact Overview
        pages = self.db.list_pages(session_id)
        console.print(f"  • Indexed Nodes: [bold cyan]{len(pages)}[/bold cyan]")

        # AI Threat Triage
        if auto_ai and pages:
            console.print("\n[bold magenta]🤖 Synthesizing AI Threat Intelligence Dossier...[/bold magenta]")
            target_page = pages[0]
            summary = self.ai_analyzer.generate_investigation_summary(
                target_page["url"],
                target_page.get("content", ""),
                target_page.get("meta", {}),
            )
            console.print(
                Panel(
                    summary,
                    title=f"🛡️ AI OSINT Assessment: {target_page['title'] or target_page['url'][:40]}",
                    border_style="magenta",
                )
            )

        # Offer Report Generation
        if Confirm.ask("\n[bold]Generate high-aesthetic forensic report dossier (HTML/JSON)?[/bold]", default=True):
            generator = ReportGenerator(db=self.db)
            outputs = generator.generate_session_report(session_id)
            console.print(f"[green]✓ HTML Dossier Generated:[/green] [cyan]{outputs['html']}[/cyan]")
            console.print(f"[green]✓ JSON Raw Data Export:[/green] [dim]{outputs['json']}[/dim]")
            if "pdf" in outputs:
                console.print(f"[green]✓ PDF Forensic File:[/green] [cyan]{outputs['pdf']}[/cyan]")

    def _guided_metasearch_mission(self) -> None:
        """Interactive dark web multi-engine meta-search wizard."""
        console.print("\n[bold cyan]═══ 🧅 DARK WEB MULTI-ENGINE META-SEARCH ═══[/bold cyan]\n")
        query = Prompt.ask("[bold]Enter Search Terms / Target Keywords[/bold]")
        if not query.strip():
            return

        console.print(f"\n[cyan]Dispatching spiders to query 11 dark web search indexes for '[bold]{query}[/bold]'...[/cyan]")
        meta = AsyncMetaSearch()

        with console.status("[bold green]Querying Ahmia, OnionLand, Torch, Kaizer, Amnesia...[/bold green]", spinner="bouncingBar"):
            results = asyncio.run(meta.search(query))

        if not results:
            console.print("[yellow]No active hidden services discovered for this query.[/yellow]")
            return

        table = Table(title=f"🔍 Discovered Hidden Services ({len(results)} Unique Nodes)")
        table.add_column("#", style="dim", width=4)
        table.add_column("Onion Service URL", style="cyan")
        table.add_column("Indexed By Engines", style="magenta")

        for idx, r in enumerate(results[:20], 1):
            table.add_row(str(idx), r["url"], ", ".join(r["found_by"]))

        console.print(table)

        if Confirm.ask("\n[bold]Launch deep crawler on top discovered targets?[/bold]", default=True):
            max_targets = IntPrompt.ask("How many top targets to crawl?", default=min(5, len(results)))
            selected_urls = [r["url"] for r in results[:max_targets]]

            session_name = generate_mission_codename()
            session_id = self.db.create_session(session_name, seed_url=f"metasearch:{query}")

            crawler = AsyncCrawler(db=self.db, depth=1, workers=5)
            console.print(f"\n[bold green]Crawl initiated for {len(selected_urls)} dark web targets...[/bold green]")
            with console.status("[bold green]Crawling targets...[/bold green]", spinner="dots"):
                asyncio.run(crawler.crawl(selected_urls))

            console.print(f"\n[bold green]✓ Meta-search crawl complete for session #{session_id}![/bold green]")

    def _guided_batch_recon(self) -> None:
        """Interactive batch target entry."""
        console.print("\n[bold cyan]═══ 📦 BATCH MULTI-TARGET RECON ═══[/bold cyan]\n")
        console.print("[dim]Enter target URLs separated by commas or whitespace:[/dim]")
        raw_input = Prompt.ask("Targets")
        urls = [sanitize_url(u.strip()) for u in raw_input.replace(",", " ").split() if u.strip()]

        if not urls:
            console.print("[red]No valid URLs provided.[/red]")
            return

        console.print(f"Loaded [bold cyan]{len(urls)}[/bold cyan] targets.")
        session_name = Prompt.ask("Session Codename", default=generate_mission_codename())
        session_id = self.db.create_session(session_name, seed_url="batch:multiple")

        crawler = AsyncCrawler(db=self.db, depth=1, workers=min(len(urls), 10))
        with console.status("[bold green]Executing batch crawl...[/bold green]", spinner="dots"):
            asyncio.run(crawler.crawl(urls))

        console.print(f"\n[bold green]✓ Batch recon finished for session #{session_id}![/bold green]")

    def _guided_ai_analysis(self) -> None:
        """Interactive AI threat triage on existing sessions."""
        console.print("\n[bold cyan]═══ 🤖 AI THREAT INTELLIGENCE LAB ═══[/bold cyan]\n")
        sessions = self.db.list_sessions()
        if not sessions:
            console.print("[yellow]No crawl sessions found in database to analyze.[/yellow]")
            return

        table = Table(title="Available Recon Sessions")
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Session Codename", style="bold white")
        table.add_column("Seed Target")
        table.add_column("Date", style="dim")

        for s in sessions[:10]:
            table.add_row(str(s["id"]), s["name"], s.get("seed_url") or "-", str(s.get("started_at", ""))[:16])
        console.print(table)

        session_id = IntPrompt.ask("Enter Session ID to Analyze")
        pages = self.db.list_pages(session_id)
        if not pages:
            console.print("[yellow]No pages found in this session.[/yellow]")
            return

        console.print(f"Session contains [bold cyan]{len(pages)}[/bold cyan] pages.")
        target_page = pages[0]

        console.print(f"\n[bold magenta]Querying AI Provider ({AI_PROVIDER.upper()})...[/bold magenta]")
        with console.status("[bold magenta]Synthesizing threat vectors & extracting intelligence...[/bold magenta]", spinner="point"):
            summary = self.ai_analyzer.generate_investigation_summary(
                target_page["url"],
                target_page.get("content", ""),
                target_page.get("meta", {}),
            )

        console.print(
            Panel(
                summary,
                title=f"🛡️ AI OSINT Threat Assessment Dossier",
                border_style="magenta",
            )
        )

    def _guided_search(self) -> None:
        """Interactive search wizard."""
        console.print("\n[bold cyan]═══ 🔍 SQLITE FTS5 FULL-TEXT SEARCH ═══[/bold cyan]\n")
        query = Prompt.ask("Search query (keywords, crypto address, email, etc.)")
        if not query.strip():
            return

        results = self.db.search_pages(query, limit=15)
        if not results:
            console.print("[yellow]No matches found in storage database.[/yellow]")
            return

        table = Table(title=f"Search Results for '{query}'")
        table.add_column("URL", style="cyan")
        table.add_column("Page Title")
        table.add_column("Language", style="dim")
        table.add_column("BM25 Score", style="magenta")

        for r in results:
            table.add_row(
                r.get("url", ""),
                r.get("title") or "Untitled",
                r.get("language") or "-",
                f"{r.get('relevance_score', 0.0):.2f}",
            )
        console.print(table)

    def _guided_report_generation(self) -> None:
        """Interactive report generation."""
        console.print("\n[bold cyan]═══ 📊 REPORT GENERATOR ═══[/bold cyan]\n")
        sessions = self.db.list_sessions()
        if not sessions:
            console.print("[yellow]No sessions found to generate report for.[/yellow]")
            return

        session_id = IntPrompt.ask("Enter Session ID")
        generator = ReportGenerator(db=self.db)
        outputs = generator.generate_session_report(session_id)
        console.print(f"[green]✓ HTML Report:[/green] [cyan]{outputs['html']}[/cyan]")
        console.print(f"[green]✓ JSON Report:[/green] [dim]{outputs['json']}[/dim]")
        if "pdf" in outputs:
            console.print(f"[green]✓ PDF Report:[/green] [cyan]{outputs['pdf']}[/cyan]")

    def _rotate_tor_ip(self) -> None:
        """Rotate Tor circuit."""
        console.print("\n[bold cyan]Requesting new Tor identity (NEWNYM signal)...[/bold cyan]")
        if renew_ip():
            time.sleep(1)
            new_ip = self.tor_manager.get_current_ip() or "Rotated (Proxy Active)"
            console.print(f"[green]✓ Tor circuit renewed! New Exit IP: [bold]{new_ip}[/bold][/green]")
        else:
            console.print("[red]✗ Unable to rotate Tor identity. Ensure Tor control port is accessible.[/red]")

    def _launch_web_ui(self) -> None:
        """Launch web server."""
        console.print("\n[bold green]🚀 Launching DeepRecon Web Command Center on http://127.0.0.1:8000[/bold green]")
        import uvicorn
        uvicorn.run("web.app:app", host="127.0.0.1", port=8000, reload=False)
