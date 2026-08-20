"""Artifact and entity extraction utilities for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import re

def extract_emails(text):
    return list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))

def extract_btc(text):
    return list(set(re.findall(r'([13][a-km-zA-HJ-NP-Z1-9]{25,34})', text)))

def extract_pgp(text):
    return list(set(re.findall(r'-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END PGP PUBLIC KEY BLOCK-----', text, re.DOTALL)))

def search_keyword(text, keyword):
    return keyword.lower() in text.lower()
