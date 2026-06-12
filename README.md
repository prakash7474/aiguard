# AI Guard CLI

AI Guard CLI is a security-first tool that protects developers from unsafe local AI agents. It monitors file access, blocks sensitive data exposure (.env, SSH keys, API tokens), enforces security policies, calculates risk scores, audits MCP interactions, and generates detailed security reports for AI-assisted development.

## Quick Start

```bash
pip install -r requirements.txt
python aiguard.py ask "fix my login bug"
```

## Commands

| Command    | Description                    |
|------------|--------------------------------|
| ask        | Ask AI with file monitoring    |
| monitor    | Start live dashboard           |
| report     | Generate security report       |
| simulate   | Attack simulation mode         |
| version    | Show version                   |
| help       | Show all commands              |
