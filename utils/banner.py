"""Visual ASCII art banner and branding for Fenrir.

Author: AIwolfie
Repository: https://github.com/AIwolfie/Fenrir
"""

from __future__ import annotations

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

try:
    from colorama import Fore, Style
    _HAS_COLORAMA = True
except ImportError:
    _HAS_COLORAMA = False

BANNER_TEXT = r"""
               __.....__        _..._           .--.         
     _.._  .-''         '.    .'     '.         |__|         
   .' .._|/     .-''"'-.  `. .   .-.   ..-,.--. .--..-,.--.  
   | '   /     /________\   \|  '   '  ||  .-. ||  ||  .-. | 
 __| |__ |                  ||  |   |  || |  | ||  || |  | | 
|__   __|\    .-------------'|  |   |  || |  | ||  || |  | | 
   | |    \    '-.____...---.|  |   |  || |  '- |  || |  '-  
   | |     `.             .' |  |   |  || |     |__|| |      
   | |       `''-...... -'   |  |   |  || |         | |      
   | |                       |  |   |  ||_|         |_|      
   |_|                       '--'   '--'                     
"""


def banner(version: str = "v3.2.0") -> None:
    """Print high-contrast Fenrir cyber banner by AIwolfie."""
    if _HAS_RICH:
        console = Console()
        text = Text(BANNER_TEXT, style="bold cyan")
        console.print(text)
        
        info_panel = Panel.fit(
            f"[bold #00f5d4]🐺 FENRIR // AUTONOMOUS DARK WEB OSINT & RECONNAISSANCE FRAMEWORK[/bold #00f5d4]\n"
            f"[dim]Version:[/dim] [bold white]{version}[/bold white]  [dim]•[/dim]  "
            f"[dim]Engine:[/dim] [bold #6366f1]Async SOCKS5 Swarm + Multi-LLM[/bold #6366f1]  [dim]•[/dim]  "
            f"[dim]Author:[/dim] [bold #10b981]AIwolfie[/bold #10b981]",
            border_style="dim cyan",
            padding=(0, 2)
        )
        console.print(info_panel)
        console.print()
    elif _HAS_COLORAMA:
        print(Fore.CYAN + BANNER_TEXT + Style.RESET_ALL)
        print(Fore.MAGENTA + f"🐺 Fenrir Framework ({version}) - Autonomous Dark Web OSINT" + Style.RESET_ALL)
        print(Fore.GREEN + "   Engineered & Maintained by AIwolfie\n" + Style.RESET_ALL)
    else:
        print(BANNER_TEXT)
        print(f"Fenrir Framework ({version}) - Autonomous Dark Web OSINT")
        print("Engineered & Maintained by AIwolfie\n")


