"""Interactive and automated entry point for Fenrir OSINT Framework.

Author: AIwolfie
Repository: https://github.com/AIwolfie/Fenrir
"""

from __future__ import annotations

import argparse
import sys

# Ensure UTF-8 output encoding on Windows consoles to prevent charmap UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console

from config import DB_PATH
from core.wizard import ReconWizard
from storage.db import FenrirDB
from utils.banner import banner
from utils.logger import configure_logging
from utils.tor_manager import TorManager

console = Console(highlight=False)


def main() -> None:
    """Entry point for Fenrir CLI, Guided Wizard, or Web UI by AIwolfie."""
    parser = argparse.ArgumentParser(
        description="🐺 Fenrir - Autonomous Dark Web OSINT & AI Threat Intelligence (by AIwolfie)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  fenrir                        # Launch Interactive Guided Wizard (Default)
  fenrir --web                  # Launch Cyber Command Web UI Dashboard
  fenrir --web --port 8080      # Launch Web UI on custom port
  fenrir --wizard               # Explicit interactive wizard launch
  fenrir --cli                  # Classic menu CLI mode
        """,
    )
    parser.add_argument("--web", action="store_true", help="Launch the Web UI Dashboard")
    parser.add_argument("--wizard", "--interactive", "-i", action="store_true", help="Launch the Interactive Guided Wizard (default)")
    parser.add_argument("--cli", action="store_true", help="Launch classic menu CLI mode")
    parser.add_argument("--host", default="127.0.0.1", help="Host address for Web UI (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port for Web UI (default: 8000)")

    args = parser.parse_args()
    configure_logging()

    if args.web:
        console.print(f"\n[bold green]Launching Fenrir Cyber Command Web UI at http://{args.host}:{args.port}[/bold green]")
        console.print("[dim]Press Ctrl+C to stop server[/dim]\n")
        import uvicorn
        uvicorn.run("web.app:app", host=args.host, port=args.port, reload=False)
        return

    db = FenrirDB(DB_PATH)
    wizard = ReconWizard(db=db)

    # Default to Interactive Guided Wizard
    wizard.run()


if __name__ == "__main__":
    main()
