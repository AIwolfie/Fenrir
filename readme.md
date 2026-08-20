<div align="center">

# 🐺 Fenrir
### *Autonomous Dark Web OSINT & AI Threat Intelligence Engine*

<p align="center">
  <a href="https://github.com/AIwolfie/Fenrir/stargazers"><img src="https://img.shields.io/github/stars/AIwolfie/Fenrir?style=for-the-badge&logo=starship&color=00f5d4&logoColor=black" alt="GitHub Stars"></a>
  <a href="https://github.com/AIwolfie/Fenrir/network/members"><img src="https://img.shields.io/github/forks/AIwolfie/Fenrir?style=for-the-badge&logo=git&color=38bdf8&logoColor=white" alt="GitHub Forks"></a>
  <a href="https://github.com/AIwolfie/Fenrir/issues"><img src="https://img.shields.io/github/issues/AIwolfie/Fenrir?style=for-the-badge&logo=github&color=a855f7&logoColor=white" alt="Issues"></a>
  <a href="https://github.com/AIwolfie/Fenrir/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-f59e0b.svg?style=for-the-badge&logo=open-source-initiative&logoColor=white" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"></a>
  <a href="https://www.torproject.org/"><img src="https://img.shields.io/badge/Tor-SOCKS5%20v3-7D4698.svg?style=for-the-badge&logo=tor-browser&logoColor=white" alt="Tor Network"></a>
  <a href="https://ollama.ai/"><img src="https://img.shields.io/badge/AI-Ollama%20%2B%20Gemini%20%2B%20GPT4o-ec4899.svg?style=for-the-badge&logo=openai&logoColor=white" alt="AI Engine"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
</p>

<p align="center">
  <b>The most aesthetic, high-velocity, and decoupled Dark Web intelligence engine on GitHub.</b><br>
  Engineered with asynchronous SOCKS5 swarms, multi-provider LLM threat contextualization, SQLite FTS5 search indexes, and modular regex extractors.
</p>

<p align="center">
  <a href="#-capabilities-radar">Capabilities</a> •
  <a href="#-key-features">Features</a> •
  <a href="#-benchmarks">Benchmarks</a> •
  <a href="#-dark-web-meta-search">Meta-Search</a> •
  <a href="#-pipeline-architecture">Architecture</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-usage-guide">Usage</a> •
  <a href="#-disclaimer">Disclaimer</a>
</p>

</div>

---

## 🎯 Capabilities Radar

<div align="center">
  <img src="https://quickchart.io/chart/render/zf-d83ff8b6-18e4-4b11-b1d5-e0341a795040" alt="Fenrir Capability Radar Chart" width="750">
</div>

---

## ✨ Key Features (Main Character Energy)

| Vector | Feature | Description |
| :--- | :--- | :--- |
| 🧠 **AI Intelligence** | **Multi-LLM Threat Triage** | Integrated with **Ollama (Llama 3)**, **Google Gemini**, **OpenAI (GPT-4o)**, **Anthropic (Claude 3.5)** & **OpenRouter**. Provides deterministic offline heuristic fallbacks when offline. |
| 🧅 **Dark Web Spider** | **Asynchronous Meta-Search** | Concurrently scans **11+ Dark Web search engines** (Ahmia, OnionLand, Torch, Kaizer, Amnesia, etc.) to discover hidden services prior to crawling. |
| ⚡ **Extreme Velocity** | **Async SOCKS5 Swarm** | Built on top of `aiohttp` + `aiohttp-socks` with rate-limiting, circuit renewal, non-blocking coroutines, and automated backoff. |
| 💰 **Artifact Harvester** | **Crypto & PGP Extraction** | Pluggable regex extractors harvest Bitcoin (`bc1`, legacy), Ethereum (`0x`), Monero (`4/8`), PGP public keys, emails, and phone numbers. |
| 🛠️ **Tech Fingerprinter** | **Stack Identification** | Detects 25+ web frameworks and servers: React, Next.js, Vue, Nuxt, FastAPI, Flask, Django, Express, WordPress, Nginx, TailwindCSS, etc. |
| 🔍 **Search Engine** | **SQLite FTS5 Full-Text** | Blazing-fast BM25 full-text search indexing across millions of scraped pages with sub-millisecond retrieval. |
| 📊 **Cyber Reports** | **Dark Cyberpunk Exports** | Automatically generates high-aesthetic HTML, JSON, and PDF forensic intelligence dossiers with copyable artifact badges. |
| 🌐 **Modern Interfaces** | **FastAPI Dashboard + CLI** | Switch effortlessly between a reactive web dashboard with live stats and an elite `rich`-powered interactive terminal console. |

---

## 📈 Benchmarks

How does Fenrir stack up against traditional crawlers? Fenrir utilizes asynchronous I/O and non-blocking SOCKS5 multiplexing to yield up to **10x higher node discovery throughput**:

<div align="center">
  <img src="https://quickchart.io/chart/render/zf-5454db70-02f8-419c-a231-3033794185d2" alt="Benchmark Speed Chart" width="750">
</div>

---

## 🧅 Dark Web Meta-Search Engine Network

Fenrir queries multiple curated onion search indexes concurrently to identify live services across disparate networks:

<div align="center">
  <img src="https://quickchart.io/chart/render/zf-9beb9cbe-85d7-479a-8ed3-337a2a65fbb6" alt="Search Engines Coverage Chart" width="750">
</div>

---

## 🏗️ Pipeline Architecture & Latency

Each scanned onion node passes through a sub-millisecond decoupled intelligence pipeline:

<div align="center">
  <img src="https://quickchart.io/chart/render/zf-8b7b877c-ee3b-48d6-9ba7-040aaeb88898" alt="Pipeline Latency Chart" width="750">
</div>


### Codebase Organization

```
Fenrir/
├── core/                  # Engine Core: SOCKS5 Async Crawler, AI Triage, Search Engines, Parser, Reporter
│   ├── ai_analyzer.py     # Multi-LLM provider router (Ollama, Gemini, OpenAI, Anthropic, Heuristics)
│   ├── crawler.py         # Async BFS crawler with rate-limiting & duplicate avoidance
│   ├── parser.py          # HTML/LXML AST entity extractor & form parser
│   ├── reporter.py        # Dark-mode Cyberpunk HTML, JSON, and PDF report builder
│   ├── search_engines.py  # 11-Engine async Dark Web meta-search dispatcher
│   └── searcher.py        # Regex & keyword intelligence scoring engine
├── plugins/               # Extensible plugin system (Drop any Python plugin here)
│   ├── crypto_detector.py # BTC (bc1/legacy), ETH, and Monero (XMR) sniffer
│   ├── email_extractor.py # Email regex pattern harvester
│   ├── fingerprinter.py   # 25+ Web server, JS framework & CMS tech identifier
│   ├── language_detector.py # NLP natural language identification
│   └── pgp_harvester.py   # PGP ASCII Armor public key block extractor
├── storage/               # Persistence Layer: SQLite FTS5 Full-Text Search
│   ├── db.py              # Schema migration, BM25 text search, link graphs, relational tables
│   └── models.py          # Dataclass entities (Site, Page, Link, KeywordHit, Session, Report)
├── utils/                 # Utilities: Tor manager, OPSEC, Rate-limiter, Banner, Logger, Validator
├── web/                   # Reactive FastAPI Web UI with Tailwind dark theme
└── tests/                 # Comprehensive pytest test suite (100% passing)
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

 🐺 Autonomous Dark Web OSINT & Intelligence Framework (v3.2.0)

 ╭─────────────────────── 🚀 Active Environment ───────────────────────╮
 │ 🐺  Fenrir OSINT Intelligence Console                                │
 │ 🧅  Tor Exit IP: 185.220.101.5 (Secure Tor Circuit)                  │
 │ 💾  Database: storage/fenrir.db                                       │
 │ 🤖  AI Provider: OLLAMA (Llama3)                                      │
 ╰──────────────────────────────────────────────────────────────────────╯

 1  Crawl direct target (.onion or clearnet)
 2  Global Dark Web Meta-Search (11 Search Engines)
 3  Search stored pages locally (FTS5 BM25 Engine)
 4  Generate AI Threat Analysis on Session
 5  Renew Tor IP (NEWNYM Signal)
 6  Generate session report (HTML / JSON / PDF)
 7  List sessions
 8  Exit
```

---

## 🚀 Quickstart

### Option 1: Docker Compose [Zero Setup - Recommended]

Spin up the entire Fenrir stack with isolated networking and persistence:

```bash
docker-compose up --build -d
```
> Open `http://localhost:8000` in your browser to access the Web UI.

---

### Option 2: Linux / Debian / Kali Linux

```bash
# Clone the repository
git clone https://github.com/AIwolfie/Fenrir.git
cd Fenrir

# Run the automated installer
chmod +x install.sh
./install.sh
```

---

### Option 3: Windows (PowerShell / CMD)

```cmd
git clone https://github.com/AIwolfie/Fenrir.git
cd Fenrir
install.bat
```

> [!TIP]
> **Windows Tor Daemon:** Ensure the [Tor Expert Bundle](https://www.torproject.org/download/tor/) is running on port `9050` (`tor.exe`).

---

## 🎮 Usage Guide

### 🌐 Mode 1: Web Dashboard

Launch the FastAPI dark-mode dashboard for point-and-click intelligence operations:

```bash
fenrir --web --port 8000
```
*Navigate to `http://localhost:8000` to monitor live crawls, explore SQLite FTS5 search indexes, and trigger AI threat summaries.*

---

### 💻 Mode 2: Interactive CLI Terminal

Stay in the terminal with rich tables, color-coded outputs, and interactive prompts:

```bash
fenrir --cli
```

---

## ⚙️ Environment Configuration (`.env`)

Fenrir reads configurations from `.env` or system environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TOR_PROXY` | `socks5h://127.0.0.1:9050` | SOCKS5 proxy endpoint for Tor traffic routing |
| `TOR_CONTROL_PORT` | `9051` | Tor control port for `NEWNYM` circuit rotation |
| `CRAWL_WORKERS` | `5` | Concurrent async coroutines for crawling |
| `CRAWL_DEPTH` | `2` | Traversal depth limit for link graph discovery |
| `CRAWL_DELAY` | `1.5` | Throttling delay between requests per worker (sec) |
| `AI_PROVIDER` | `ollama` | Provider: `ollama`, `gemini`, `openai`, `anthropic`, `openrouter` |
| `AI_MODEL` | `llama3` | Model identifier (e.g. `llama3`, `gemini-1.5-flash`, `gpt-4o`) |
| `GEMINI_API_KEY` | `""` | Google Gemini API Key |
| `OPENAI_API_KEY` | `""` | OpenAI API Key |
| `ANTHROPIC_API_KEY`| `""` | Anthropic API Key |
| `ENABLE_PDF_EXPORT`| `false` | Enable automatic WeasyPrint PDF report rendering |

---

## 🧪 Testing

Run the automated pytest test suite (covers AI heuristics, SQLite FTS5, regex extractors, plugins, reporters, and FastAPI endpoints):

```bash
pytest -v
```

```text
======================== 23 passed in 11.85s =======================
```

---

## ⚠️ Disclaimer & OPSEC Hygiene

> [!WARNING]
> This framework is developed strictly for **authorized security research, defensive threat intelligence, and educational OSINT exploration**. Interacting with arbitrary dark web services may carry legal and operational hazards depending on your jurisdiction. The authors and contributors assume no liability for misuse.
> 
> **Mandatory OPSEC Rules:**
> 1. Always execute in dedicated virtualized sandbox environments.
> 2. Verify Tor circuit status before commencing scraping.
> 3. Never reuse personal credentials or clearnet identities.

---

## 🤝 Contributing

Contributions make open source goated! Feel free to submit PRs for new search engines, plugin extractors, or frontend features:

1. Fork the repo (`git checkout -b feature/EpicPlugin`)
2. Commit your upgrades (`git commit -m 'feat: Add Monero subaddress tracker'`)
3. Push to your branch (`git push origin feature/EpicPlugin`)
4. Open a Pull Request

---

## 🌟 Support the Project
 
 <div align="center">
   <a href="https://github.com/AIwolfie/Fenrir/stargazers"><img src="https://img.shields.io/github/stars/AIwolfie/Fenrir?style=for-the-badge&logo=github&color=00f5d4&logoColor=black&label=Stars" alt="Stars"></a>
   &nbsp;
   <a href="https://github.com/AIwolfie/Fenrir/network/members"><img src="https://img.shields.io/github/forks/AIwolfie/Fenrir?style=for-the-badge&logo=git&color=a855f7&logoColor=white&label=Forks" alt="Forks"></a>
   &nbsp;
   <a href="https://github.com/AIwolfie/Fenrir/watchers"><img src="https://img.shields.io/github/watchers/AIwolfie/Fenrir?style=for-the-badge&logo=eye&color=38bdf8&logoColor=white&label=Watchers" alt="Watchers"></a>
 
   <br><br>
   <b>Created & Maintained by <a href="https://github.com/AIwolfie">AIwolfie</a></b><br>
   <i>If Fenrir helped your research, smash that ⭐ — it keeps the project alive and motivates new features!</i>
 </div>

---

## 💖 Acknowledgements

- The **Tor Project** for open-source anonymity networks.
- The **FastAPI** and **Rich** ecosystems for making terminal and web tooling effortless.

---

## 📝 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for terms.