"""OPSEC safety guidelines for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

from colorama import Fore, Style

def opsec_warning():
    print(Fore.RED + "\n[!] OPSEC WARNING: Stay anonymous!")
    print("- Use a VPN + Tor")
    print("- Never use real identity")
    print("- Do NOT click unknown links" + Style.RESET_ALL)
