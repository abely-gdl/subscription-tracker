# Subscription Tracker — Developer Guide

## Overview

AI training project demonstrating Claude Code + MCP integration.
Domain: manage personal subscriptions (Netflix, Spotify, etc.) with CRUD, cost analysis, and budget advice.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Developer                             │
└──────────────────────────────┬───────────────────────────────┘
                               │ types in Claude Code
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                      Claude Code CLI                         │
│  Skills: /cost-report  /spending-forecast                    │
│  Sub-agents: budget-advisor                                  │
│  Hooks: pre-edit secrets check · post-edit Python syntax     │
└──────────────────────────────┬───────────────────────────────┘
                               │ MCP protocol (stdio)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│              MCP Server  (Python / FastMCP)                  │
│  6 tools · 4 resources · 2 prompts                           │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP + X-Api-Key header
                               ▼
┌──────────────────────────────────────────────────────────────┐
│            .NET 9 Minimal API  (C#)                          │
│  CRUD /subscriptions  ·  /health                             │
└──────────────────────────────┬───────────────────────────────┘
                               │ EF Core
                               ▼
┌──────────────────────────────────────────────────────────────┐
│              SQLite  (subscriptions.db)                      │
└──────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
ai-sdlc/
├── .claude/
│   ├── settings.json          MCP server config + hooks
│   ├── commands/
│   │   ├── cost-report.md     /cost-report skill
│   │   └── spending-forecast.md  /spending-forecast skill
│   └── agents/
│       └── budget-advisor.md  budget-advisor sub-agent
├── hooks/
│   ├── check_secrets.py       pre-edit: block hardcoded credentials
│   └── check_python_syntax.py post-edit: py_compile check on .py files
├── backend/
│   └── SubscriptionTracker.Api/
│       ├── Data/              EF Core DbContext
│       ├── Endpoints/         Minimal API route handlers
│       ├── Middleware/        API key auth
│       └── Models/            Domain types + DTOs
├── mcp-server/
│   ├── server.py              FastMCP server (tools, resources, prompts)
│   └── api_client.py          HTTP wrapper for the .NET API
└── http-tests/
    └── subscriptions.http     VS Code REST Client test file
```

## Prerequisites

- .NET 9 SDK
- Python 3.11+
- Node.js (for MCP Inspector only)

## Starting the Backend

```bash
cd backend/SubscriptionTracker.Api
dotnet run
# Listens on http://localhost:5000
```

First run creates `subscriptions.db` automatically via EF Core.

## Starting the MCP Server

```bash
cd mcp-server
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

The MCP server is configured in `.claude/settings.json` and starts automatically when Claude Code loads.

## API Authentication and Secrets

The .NET API requires an `X-Api-Key` header on every request (except `/health`).

**How the key flows:**

| Component | Where the key lives |
|-----------|-------------------|
| .NET API (validates) | `appsettings.Development.json` → `"ApiKey"` |
| MCP server (sends) | `mcp-server/.env` → `API_KEY` |
| Claude Code → MCP | `.claude/settings.json` → `env.API_KEY` |

Both sides must use the **same value**. The default dev key is `dev-secret-key-change-me`.

**Setup:**
```bash
# .NET side
cp backend/SubscriptionTracker.Api/appsettings.Development.json.example \
   backend/SubscriptionTracker.Api/appsettings.Development.json
# Edit and set your ApiKey value

# MCP side
cp mcp-server/.env.example mcp-server/.env
# Edit and set the same API_KEY value
```

Neither file is committed to git.

## Domain Model

```
Subscription {
  Id           Guid
  Name         string (required)
  Cost         decimal
  BillingCycle Monthly | Annual
  Category     string (required)
  RenewalDate  DateOnly (YYYY-MM-DD)
  Status       Active | Paused | Cancelled
}
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_all_subscriptions` | All subscriptions |
| `get_subscription` | Single subscription by ID |
| `add_subscription` | Create new subscription |
| `update_subscription` | Partial update by ID |
| `delete_subscription` | Delete by ID |
| `get_subscriptions_by_category` | Filter by category |

## MCP Resources

| Resource | Description |
|----------|-------------|
| `subscriptions://all` | All subscriptions as JSON |
| `subscriptions://active` | Active subscriptions only |
| `subscriptions://expiring-soon` | Renewals due within 7 days |
| `subscriptions://monthly-cost` | Aggregated monthly cost by category |

## MCP Prompts

| Prompt | Description |
|--------|-------------|
| `monthly_summary` | Generates a monthly spending report |
| `renewal_alerts` | Lists upcoming renewals (7-day window) |

## Skills

| Command | Description |
|---------|-------------|
| `/cost-report` | Spending breakdown by category and billing period |
| `/spending-forecast` | 12-month cost projection based on renewal dates |

## Sub-agents

| Agent | Description |
|-------|-------------|
| `budget-advisor` | Detects duplicate subscriptions, computes billing-switch savings, lists cancellation candidates |

## Hooks

| Hook | Trigger | Action |
|------|---------|--------|
| Pre-edit | Any file edit | Scans new content for hardcoded credentials; blocks if found |
| Post-edit | Any file edit | Runs `py_compile` on `.py` files; surfaces syntax errors immediately |

## Testing

```bash
# MCP Inspector (all tools, resources, prompts)
npx @modelcontextprotocol/inspector python mcp-server/server.py

# HTTP tests (VS Code REST Client)
# Open http-tests/subscriptions.http

# Verify auth
curl http://localhost:5000/subscriptions             # → 401
curl http://localhost:5000/subscriptions \
  -H "X-Api-Key: dev-secret-key-change-me"          # → 200
curl http://localhost:5000/health                    # → 200 (no auth)
```

## Conventions

- **C#**: sealed classes, record DTOs, `required` modifier on non-nullable strings
- **Python**: `logging` for all output (never `print`), type hints on all functions
- **Secrets**: never hardcoded — always `.env` or `appsettings.Development.json`
- **Commits**: one logical layer per commit; no auto-push
