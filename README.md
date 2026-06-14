# AI Guard CLI

**The Antivirus for Local AI Coding Agents** — security layer between developers and local AI assistants (Ollama, LM Studio, OpenCode).

Monitors every file the AI reads, blocks sensitive data leaks, detects secrets, and gives you full visibility into AI agent behavior.

---

## Quick Start

```bash
pip install -r requirements.txt

# Ask AI with file access monitoring (Ollama)
python -m aiguard ask "explain binary search"

# Scan a file for secrets
python -m aiguard scan file .env

# Scan text content
python -m aiguard scan content "AWS_ACCESS_KEY=AKIA1234567890ABCDEF"

# Run attack simulation
python -m aiguard simulate
```

---

## Table of Contents

- [How It Works](#how-it-works)
- [CLI Commands](#cli-commands)
- [Secret Detection](#secret-detection)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Testing](#testing)
- [Development Phases](#development-phases)
- [Windows Limitations](#windows-limitations)
- [Troubleshooting](#troubleshooting)

---

## How It Works

When you run `aiguard ask`, it:

1. **Hooks Python's `open()`** to intercept every file read the AI makes
2. **Checks policy** — blocks access to `.env`, SSH keys, credentials
3. **Runs Ollama** locally — no cloud API keys, no OpenAI dependency
4. **Logs all access** — tracks every file read/write/block in a session
5. **Shows summary** — files read, blocked, duration, security score

### Security Flow

```
AI Agent (Ollama/OpenCode)
    │
    ▼
File Access ──► Policy Check ──► ALLOW / BLOCK
    │
    ▼
Secret Detection ──► Scan Content ──► [REDACTED]
    │
    ▼
Session Log ──► Summary Report
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `ask "prompt"` | Run Ollama with file read interception |
| `monitor` | Start live file monitoring (writes/creates/deletes via watchdog) |
| `scan file <path>` | Scan a file for secrets |
| `scan content <text>` | Scan text content for secrets |
| `scan dir <path>` | Scan a directory for secrets |
| `report` | Generate HTML security report |
| `simulate` | Run attack simulation (7 attack scenarios) |
| `version` | Show version |
| `help` | Show all commands |

### Full Command Reference

```bash
# Help
python -m aiguard help

# Version
python -m aiguard version

# Ask AI Guard (Ollama)
python -m aiguard ask "your question"
python -m aiguard ask "How to fix login bug?" --path ./project
python -m aiguard ask "Explain this code" --model llama3.2:3b

# Monitor files
python -m aiguard monitor
python -m aiguard monitor --path ./my-project
python -m aiguard monitor --quiet

# Scan secrets
python -m aiguard scan file .env
python -m aiguard scan file config.py --redact
python -m aiguard scan content "API_KEY=sk-xxxx"
python -m aiguard scan content "PASSWORD=test" --redact
python -m aiguard scan dir ./project
python -m aiguard scan dir ./project --no-recursive

# Simulate attack
python -m aiguard simulate

# Generate HTML report
python -m aiguard report
```

---

## Secret Detection

> **No OpenAI API key patterns** — designed for local AI (Ollama). Detects secrets that actually matter on a developer machine.

### Severity Levels

| Severity | Types Detected |
|----------|----------------|
| **CRITICAL** | AWS Access Keys, AWS Secret Keys, GitHub Tokens, GitHub OAuth, Google API Keys, Stripe Keys, Private Keys (RSA/DSA/EC/OPENSSH), SSH Keys (id_rsa/ed25519), Database Passwords (MySQL/PostgreSQL/MongoDB/Redis), Slack Tokens |
| **HIGH** | JWT Tokens, `.env` files, `.env.local`, `.env.production`, `credentials.json`, Firebase Admin Keys, PEM certificates, `.key` files |

### Usage Examples

```bash
# Scan .env file
$ python -m aiguard scan file .env
SECRETS DETECTED
┌───────────────┬──────────────────────┬──────────┬──────┐
│ Type          │ Description          │ Severity │ Line │
├───────────────┼──────────────────────┼──────────┼──────┤
│ db_password   │ Database Password    │ CRITICAL │ 1    │
│ aws_access_key│ AWS Access Key ID    │ CRITICAL │ 2    │
└───────────────┴──────────────────────┴──────────┴──────┘

# Scan text content with redaction
$ python -m aiguard scan content "DATABASE_PASSWORD=secret123" --redact
DATABASE_PASSWORD=[REDACTED]
```

---

## Architecture

### High-Level Design

```
User (CLI)
    │
    ▼
┌─────────────────────────────────────────────┐
│           AI Guard CLI (aiguard.py)         │
├──────────┬──────────┬──────────┬────────────┤
│ ask cmd  │ monitor  │ scan cmd │ simulate   │
│ (intercept│ (watchdog)│ (regex) │ (policy    │
│  open()) │          │          │  checks)   │
└─────┬────┴────┬─────┴────┬─────┴─────┬──────┘
      │         │          │           │
      ▼         ▼          ▼           ▼
  Ollama    File Sys   Files/     Security
  (local)   Events     Content    Policies
```

### Component Layers

| Layer | Technology | Status |
|-------|-----------|--------|
| CLI Framework | Typer | ✅ |
| Terminal UI | Rich (Panels, Tables) | ✅ |
| File Monitoring | Watchdog (writes/creates/deletes) | ✅ |
| File Read Interception | Python `open()` hook | ✅ |
| Secret Detection | Regex patterns | ✅ |
| AI Integration | Ollama Python library | ✅ |
| Session Storage | SQLite | 🔒 Phase 6 |
| HTML Reports | Jinja2 | 🔒 Phase 7 |

---

## Project Structure

```
aiguard/
├── aiguard.py                  # Main CLI entry point (Typer app)
├── requirements.txt            # Dependencies
├── setup.py                    # Package install config
├── README.md                   # This file
│
├── cli/
│   ├── ask.py                  # ask command — file intercept + Ollama
│   ├── monitor.py              # monitor command — watchdog wrapper
│   ├── scan.py                 # scan subcommands (file/content/dir)
│   ├── simulate.py             # simulate command — attack demo
│   └── report.py               # report command (placeholder)
│
├── monitor/
│   ├── file_watcher.py         # Watchdog-based file monitor
│   └── file_access_interceptor.py  # Python open() hook + hybrid monitor
│
├── security/
│   ├── secret_scanner.py       # Regex-based secret detection
│   └── policy_manager.py       # File access policy rules
│
├── database/
│   └── session_db.py           # SQLite session storage (Phase 6)
│
├── report/
│   └── html_generator.py       # HTML report template
│
├── ai/
│   ├── ollama_runner.py        # Ollama chat integration
│   └── __init__.py
│
├── sessions/                   # Session data storage
├── reports/                    # Generated HTML reports
└── tests/                      # Test files
```

---

## Installation

### Prerequisites

- Python 3.8+
- Ollama (for `ask` command) — [ollama.ai](https://ollama.ai)

### Setup

```bash
# Clone or create the project
mkdir aiguard && cd aiguard

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m aiguard version
python -m aiguard help
```

### Dependencies

```
typer>=0.12.0      # CLI framework
rich>=13.7.0       # Terminal output (colors, tables, panels)
watchdog>=4.0.0    # File system event monitoring
jinja2>=3.1.0      # HTML report templates
ollama>=0.4.0      # Local AI integration
```

---

## Testing

### Test Commands

```bash
# Test CLI
python -m aiguard version
python -m aiguard help

# Test ask (with Ollama running)
python -m aiguard ask "hello in 5 words"

# Test secret scanning
echo "DATABASE_PASSWORD=secret123" > .env
python -m aiguard scan file .env
python -m aiguard scan content "AWS_ACCESS_KEY=AKIA1234567890ABCDEF"
python -m aiguard scan content "DB_PASSWORD=test" --redact
python -m aiguard scan dir . --no-recursive

# Test attack simulation
python -m aiguard simulate
```

### Expected Output

```
# Simulate output: 7/7 passed (100%)
┌──────────────────────────────────────────────┐
│ Attack Simulation Results                    │
├──────────┬──────────────────┬────────┬───────┤
│ Attack   │ File             │ Result │ Expect│
├──────────┼──────────────────┼────────┼───────┤
│ PASS     │ .env             │ BLOCKED│ BLOCKED│
│ PASS     │ id_rsa           │ BLOCKED│ BLOCKED│
│ PASS     │ credentials.json │ BLOCKED│ BLOCKED│
│ PASS     │ cert.pem         │ BLOCKED│ BLOCKED│
│ PASS     │ src/App.py       │ ALLOWED│ ALLOWED│
│ PASS     │ Header.jsx       │ ALLOWED│ ALLOWED│
│ PASS     │ README.md        │ ALLOWED│ ALLOWED│
└──────────┴──────────────────┴────────┴───────┘
```

---

## Development Phases

### Phase 1: CLI Basics ✅ COMPLETE

| Feature | Status | Command |
|---------|--------|---------|
| Typer CLI Framework | ✅ | All commands |
| Rich Terminal Output | ✅ | Colors, panels, tables |
| `ask` command | ✅ | `aiguard ask "prompt"` |
| `monitor` command | ⚠️ Partial | Writes yes, reads no (Windows) |
| `report` command | ✅ | `aiguard report` |
| `simulate` command | ✅ | `aiguard simulate` |
| `version` command | ✅ | `aiguard version` |
| `help` command | ✅ | `aiguard help` |

### Phase 2: File Monitor ⚠️ PARTIAL

| Feature | Status | Windows? |
|---------|--------|----------|
| WRITE monitoring | ✅ | Yes (watchdog) |
| CREATE monitoring | ✅ | Yes (watchdog) |
| DELETE monitoring | ✅ | Yes (watchdog) |
| READ monitoring | ❌ | No (Windows limitation) |

### Phase 3: Secret Detection ✅ COMPLETE

| Feature | Status | Command |
|---------|--------|---------|
| API Key Detection | ✅ | AWS, GitHub, Google, Stripe |
| Password Detection | ✅ | DB passwords (MySQL, PostgreSQL) |
| SSH Key Detection | ✅ | id_rsa, id_ed25519 |
| Secret File Detection | ✅ | .env, credentials.json, .pem |
| Content Scanning | ✅ | `aiguard scan content "text"` |
| File Scanning | ✅ | `aiguard scan file .env` |
| Directory Scanning | ✅ | `aiguard scan dir ./project` |
| Secret Redaction | ✅ | `--redact` flag |

### Phase 4-9 🔒 LOCKED

| Phase | Feature | Status |
|-------|---------|--------|
| 4 | Policy Engine (interactive permissions) | 🔒 |
| 5 | Live Dashboard (real-time UI) | 🔒 |
| 6 | Session Recording (SQLite) | 🔒 |
| 7 | HTML Reports (Jinja2 templates) | 🔒 |
| 8 | Attack Simulation (real AI testing) | 🔒 |
| 9 | AI Integration (full proxy) | 🔒 |

---

## Windows Limitations

### File Read Tracking

Windows does not expose file **READ** events through filesystem APIs. This is a Windows OS limitation.

| Operation | Windows Support | macOS/Linux Support |
|-----------|----------------|---------------------|
| WRITE tracking | ✅ Watchdog | ✅ Watchdog |
| CREATE tracking | ✅ Watchdog | ✅ Watchdog |
| DELETE tracking | ✅ Watchdog | ✅ Watchdog |
| READ tracking | ❌ Not possible | ✅ kqueue/inotify |

### Our Solution: Python `open()` Hook

We bypass this by **hooking Python's built-in `open()` function**. This works when:

- The AI agent runs **inside Python** (e.g., via `ollama` Python library)
- `aiguard ask` wraps the Ollama call with the interceptor

For external AI processes (OpenCode CLI), READ tracking is currently limited on Windows.

---

## Troubleshooting

### Module Not Found

```bash
# Error: ModuleNotFoundError: No module named 'typer'
pip install typer rich watchdog
```

### Ollama Not Running

```bash
# Error when running `aiguard ask`
# Make sure Ollama is running:
ollama serve

# Pull a model if needed:
ollama pull llama3.2:3b

# Test Ollama directly:
python testlocalllm.py
```

### Secrets Not Detected

```bash
# Check file encoding (PowerShell echo creates UTF-16)
# Use Set-Content -Encoding ASCII instead:
Set-Content -Path ".env" -Value "DB_PASSWORD=test" -Encoding ASCII

# Run scan:
python -m aiguard scan file .env
```

---

## Quick Reference

```bash
# All available commands
python -m aiguard help

# Ask AI (Ollama) with file monitoring
python -m aiguard ask "fix my login bug"

# Monitor file changes
python -m aiguard monitor

# Scan secrets
python -m aiguard scan file .env
python -m aiguard scan content "PASSWORD=test"
python -m aiguard scan dir ./project

# Simulate attacks
python -m aiguard simulate

# Generate report
python -m aiguard report

# Version info
python -m aiguard version
```
