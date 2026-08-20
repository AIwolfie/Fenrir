<div align="center">

```
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
```

# 🐺 FENRIR
### *Next-Gen Autonomous Dark Web Reconnaissance, SOCKS5 Multiplexing & Multi-LLM Threat Triage*

<p align="center">
  <a href="https://github.com/AIwolfie/Fenrir/stargazers"><img src="https://img.shields.io/badge/Stars-⭐%20Rate%20Repo-00f5d4?style=for-the-badge&logo=github&logoColor=black" alt="GitHub Stars"></a>
  <a href="https://github.com/AIwolfie/Fenrir/network/members"><img src="https://img.shields.io/badge/Forks-🍴%20Fork%20Repo-38bdf8?style=for-the-badge&logo=git&logoColor=white" alt="GitHub Forks"></a>
  <a href="https://github.com/AIwolfie/Fenrir/issues"><img src="https://img.shields.io/badge/Issues-🐛%20Active-a855f7?style=for-the-badge&logo=github&logoColor=white" alt="Issues"></a>
  <a href="https://github.com/AIwolfie/Fenrir/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-f59e0b.svg?style=for-the-badge&logo=open-source-initiative&logoColor=white" alt="License"></a>
</p>
<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"></a>
  <a href="https://www.torproject.org/"><img src="https://img.shields.io/badge/Tor-SOCKS5%20v3-7D4698.svg?style=for-the-badge&logo=tor-browser&logoColor=white" alt="Tor Network"></a>
  <a href="https://ollama.ai/"><img src="https://img.shields.io/badge/AI-Ollama%20%2B%20Gemini%20%2B%20GPT4o-ec4899.svg?style=for-the-badge&logo=openai&logoColor=white" alt="AI Engine"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
</p>

<p align="center">
  <b>An elite, modular intelligence platform designed for defensive cyber threat investigations, cryptocurrency tracing, and hidden service mapping across the encrypted web.</b>
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-core-capabilities">Capabilities</a> •
  <a href="#-architecture--workflow">Architecture</a> •
  <a href="#-quickstart-installation">Installation</a> •
  <a href="#-usage-guide">Usage</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-opsec--disclaimer">OPSEC</a>
</p>

</div>

---

## ⚡ Overview

**Fenrir** is an autonomous intelligence gathering engine designed to illuminate dark web infrastructures. Named after the mythical wolf of unyielding strength, Fenrir sweeps hidden services (`.onion`), harvests critical forensic artifacts, indexes contents using high-speed BM25 search, and leverages local or cloud LLMs to synthesize automated threat dossiers.

---

## 🚀 Core Capabilities

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 🐺 FENRIR CORE SUITE                    │
                  └────────────────────────────┬────────────────────────────┘
                                               │
      ┌────────────────────┬───────────────────┼───────────────────┬────────────────────┐
      ▼                    ▼                   ▼                   ▼                    ▼
[ 🧅 Meta-Search ]  [ ⚡ Async Swarm ]  [ 💰 Harvester ]   [ 🔍 FTS5 Engine ]   [ 🤖 Multi-LLM ]
Concurrently scans   Non-blocking SOCKS5  Extracts BTC, ETH, Sub-millisecond      Auto-generates
11+ Onion Search     BFS crawler with     Monero, Emails &   full-text search     threat dossiers
Engines in parallel  circuit rotation     PGP armor blocks   across stored nodes  via Ollama/Gemini
```

### 💎 Tactical Features Matrix

| Module | Operational Vector | Description |
| :--- | :--- | :--- |
| 🧅 **Dark Discovery** | **Multi-Index Meta-Search** | Concurrently queries 11+ Dark Web search engines (Ahmia, Torch, Kaizer, Amnesia, etc.) to discover active `.onion` hosts before crawling. |
| ⚡ **Async Spider** | **SOCKS5 Swarm Multiplexing** | Built on non-blocking `aiohttp` + `aiohttp-socks` with dynamic rate-limiting, traversal depth controls, and transient Tor drop recovery. |
| 💰 **Forensic Harvester**| **Multi-Asset Extraction** | Specialized regex engines sniff Bitcoin (`bc1` & legacy), Ethereum (`0x`), Monero (`4/8`), PGP public keys, emails, and phone numbers. |
| 🛠️ **Tech Profiler** | **Stack Identification** | Fingerprints 25+ technologies including Nginx, Apache, FastAPI, Django, Flask, Express, React, Next.js, WordPress, and TailwindCSS. |
| 🔍 **Search Engine** | **SQLite FTS5 Full-Text** | Blazing-fast BM25 full-text search indexing across millions of scraped pages with sub-millisecond retrieval. |
| 🤖 **Threat Triage** | **Multi-LLM Synthesis** | Summarizes crawled targets using **Ollama (Llama 3)**, **Google Gemini**, **OpenAI (GPT-4o)**, or deterministic offline heuristics. |
| 📊 **Cyber Dossiers** | **Forensic Dossier Exports** | Builds high-aesthetic dark cyberpunk dossiers in HTML, JSON, and optional PDF formats. |
| 🌐 **Modern Command** | **FastAPI HUD + CLI Wizard** | Switch seamlessly between an obsidian-cyan web dashboard and an interactive terminal mission control. |

---

## 🏗️ Architecture & Workflow

```
[ Target Input / Search Query ]
              │
              ▼
[ Tor SOCKS5 Layer (socks5h://127.0.0.1:9050) ] ──▶ Remote DNS Resolution & NEWNYM Circuit Rotation
              │
              ▼
[ Async Crawler Engine (core/crawler.py) ]     ──▶ BFS Depth Traversal & Throttled Workers
              │
              ▼
[ Modular Plugins Pipeline (plugins/) ]        ──▶ Crypto, Emails, PGP, Tech Stack, NLP Language
              │
              ▼
[ Persistence Engine (storage/db.py) ]         ──▶ SQLite FTS5 Full-Text Indexing (storage/fenrir.db)
              │
              ▼
[ Multi-LLM Threat Analyzer (core/ai_analyzer.py) ] ──▶ Automated Threat Dossier Synthesis
              │
              ▼
[ Output Layer ]                               ──▶ Web UI Dashboard / Interactive CLI / Cyberpunk Reports
```

---

## 💻 CLI Terminal Preview

```
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

 🐺 Fenrir OSINT Intelligence Console (v3.2.0)

 ╭─────────────────────── 🚀 Active Environment ───────────────────────╮
 │ 🐺  Mission Control: Fenrir Threat Operations                        │
 │ 🧅  Tor Exit IP: 185.220.101.5 (Encrypted SOCKS5 Circuit)            │
 │ 💾  Storage Database: storage/fenrir.db                              │
 │ 🤖  AI Engine: Ollama (Llama 3) / Google Gemini                      │
 ╰──────────────────────────────────────────────────────────────────────╯

 1  🎯 Interactive Recon Mission (Guided Crawler)
 2  🧅 Dark Web Meta-Search Infiltration (11 Engines)
 3  📦 Batch Multi-Target Recon
 4  🤖 AI Threat Intelligence Analysis
 5  🔍 SQLite FTS5 Local Search (BM25 Index)
 6  📊 Generate Forensic Dossier Report (HTML/JSON/PDF)
 7  🔄 Rotate Tor Identity (NEWNYM Signal)
 8  🌐 Launch Modern Web UI Dashboard
 9  🚪 Exit Console
```

---

## 🚀 Quickstart & Installation

### Option 1: Windows (Automated Setup)

```cmd
git clone https://github.com/AIwolfie/Fenrir.git
cd Fenrir
install.bat
```

> [!TIP]
> **Windows Tor Daemon:** Ensure the [Tor Expert Bundle](https://www.torproject.org/download/tor/) or Tor Browser is running on port `9050` (`tor.exe`).

---

### Option 2: Linux / Kali Linux / Debian

```bash
# Clone the repository
git clone https://github.com/AIwolfie/Fenrir.git
cd Fenrir

# Run automated installer
chmod +x install.sh
./install.sh
```

---

### Option 3: Docker Container [Zero Setup]

```bash
docker-compose up --build -d
```
> Navigate to `http://localhost:8000` to access the Cyber Command Dashboard.

---

## 🎮 Usage Guide

### 🌐 Mode 1: Cyber Command Web UI
Launch the reactive FastAPI dashboard:
```bash
fenrir --web
```
*Or customize host and port:*
```bash
fenrir --web --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000` in any browser to launch live crawlers, run FTS5 queries, and review AI threat summaries.

---

### 💻 Mode 2: Interactive Terminal Wizard
Launch the guided step-by-step console:
```bash
fenrir
```
*Or explicitly with:*
```bash
fenrir --wizard
# or classic menu
fenrir --cli
```

---

## ⚙️ Configuration (`.env`)

Fenrir reads configuration from `.env` or system environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TOR_PROXY` | `socks5h://127.0.0.1:9050` | SOCKS5 proxy endpoint for Tor traffic routing |
| `TOR_CONTROL_PORT` | `9051` | Tor control port for `NEWNYM` circuit rotation |
| `CRAWL_WORKERS` | `5` | Concurrent async coroutines for crawling |
| `CRAWL_DEPTH` | `2` | Traversal depth limit for link graph discovery |
| `CRAWL_DELAY` | `1.5` | Throttling delay between requests per worker (sec) |
| `DB_PATH` | `storage/fenrir.db` | SQLite database file location |
| `AI_PROVIDER` | `ollama` | Provider: `ollama`, `gemini`, `openai`, `anthropic`, `openrouter` |
| `AI_MODEL` | `llama3` | Model identifier (e.g. `llama3`, `gemini-1.5-flash`, `gpt-4o`) |
| `GEMINI_API_KEY` | `""` | Google Gemini API Key |
| `OPENAI_API_KEY` | `""` | OpenAI API Key |
| `ANTHROPIC_API_KEY`| `""` | Anthropic API Key |
| `ENABLE_PDF_EXPORT`| `false` | Enable automatic WeasyPrint PDF report rendering |

---

## ⚠️ OPSEC & Legal Disclaimer

> [!WARNING]
> **Defensive & Research Notice:** Fenrir is engineered strictly for **authorized security research, defensive threat intelligence, incident response, and academic OSINT exploration**. Navigating the dark web carries legal and operational responsibilities. The authors and contributors assume no liability for misuse.
> 
> **Mandatory OPSEC Rules:**
> 1. Execute only inside virtualized sandboxes or isolated containers.
> 2. Always confirm Tor SOCKS5 circuit health before commencing operations.
> 3. Never reuse real identities, credentials, or personal payment methods.

---

## 🐺 Author & Support

<div align="center">
  <b>Designed, Engineered & Maintained by <a href="https://github.com/AIwolfie">AIwolfie</a></b><br><br>
  <i>If Fenrir assists your threat intelligence workflow, give the repository a ⭐ to support future releases!</i>
</div>

---

## 📝 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for complete terms.