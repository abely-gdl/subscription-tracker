# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

AI training project demonstrating Claude Code + MCP integration.
Domain: manage personal subscriptions (Netflix, Spotify, etc.) with CRUD, cost analysis, and budget advice.

The stack is: Claude Code CLI → MCP Server (Python/FastMCP, stdio) → .NET 9 Minimal API → SQLite via EF Core.

## Prerequisites

- .NET 9 SDK
- Python 3.11+
- Node.js (for MCP Inspector only)

## Commands

```bash
# Start the backend (http://localhost:5000)
cd backend/SubscriptionTracker.Api
dotnet run

# Build only (post-edit hook also runs this automatically)
dotnet build backend/SubscriptionTracker.Api --no-restore

# Start the MCP server (auto-started by Claude Code via settings.json)
cd mcp-server
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python server.py

# MCP Inspector (interactive tool/resource/prompt testing)
npx @modelcontextprotocol/inspector python mcp-server/server.py

# Verify auth
curl http://localhost:5000/subscriptions                          # → 401
curl http://localhost:5000/subscriptions -H "X-Api-Key: dev-secret-key-change-me"  # → 200
curl http://localhost:5000/health                                 # → 200 (no auth)
```

## API Authentication Setup

The .NET API requires `X-Api-Key` on every request (except `/health`). Both sides must share the same key value.

| Component | Where the key lives |
|-----------|-------------------|
| .NET API (validates) | `appsettings.Development.json` → `"ApiKey"` |
| MCP server (sends) | `mcp-server/.env` → `API_KEY` |

```bash
cp backend/SubscriptionTracker.Api/appsettings.Development.json.example \
   backend/SubscriptionTracker.Api/appsettings.Development.json

cp mcp-server/.env.example mcp-server/.env
# Edit both files to use the same key value
```

Neither file is committed to git.

## Domain Model

```
Subscription {
  Id           Guid (EF Core generates on add)
  Name         string (required)
  Cost         decimal
  BillingCycle Monthly | Annual
  Category     string (required)
  RenewalDate  DateOnly (YYYY-MM-DD)
  Status       Active | Paused | Cancelled
}
```

Enums are stored as strings in SQLite (configured via `HasConversion<string>()` in `AppDbContext`). The .NET JSON serializer uses `JsonStringEnumConverter`, so enums serialize as `"Monthly"`, `"Active"`, etc.

## Non-obvious Architecture

**MCP → API field mapping**: Python tool parameters use `snake_case` (`billing_cycle`, `renewal_date`); `api_client.py` sends camelCase JSON (`billingCycle`, `renewalDate`). If you add a new field, update both.

**DELETE returns 204**: `api_client.py` checks `response.status_code == 204` (not `raise_for_status`) and returns a bool. All other methods call `raise_for_status()`.

**Monthly cost resource**: Only `Active` subscriptions count. Annual costs are divided by 12 for the monthly-equivalent breakdown in `subscriptions://monthly-cost`.

**Spending forecast**: Monthly subscriptions add cost every month for 12 months. Annual subscriptions add the full cost only in the calendar month where `renewal_date`'s day-of-month matches.

**Port note**: `appsettings.json` binds to `http://localhost:5000`; `launchSettings.json` profiles use 5183/7083. `dotnet run` without a profile uses 5000.

## MCP Surface

**Tools**

| Tool | Maps to |
|------|---------|
| `get_all_subscriptions` | `GET /subscriptions` |
| `get_subscription` | `GET /subscriptions/{id}` |
| `add_subscription` | `POST /subscriptions` |
| `update_subscription` | `PUT /subscriptions/{id}` |
| `delete_subscription` | `DELETE /subscriptions/{id}` |
| `get_subscriptions_by_category` | `GET /subscriptions/category/{category}` |

**Resources**

| Resource | Description |
|----------|-------------|
| `subscriptions://all` | All subscriptions as JSON |
| `subscriptions://active` | Active subscriptions only |
| `subscriptions://expiring-soon` | Renewals due within 7 days |
| `subscriptions://monthly-cost` | Aggregated monthly cost by category |

**Prompts**

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
| `api-contract-checker` | Checks MCP tool definitions in `server.py` stay in sync with .NET API endpoints — detects field name, route, and type mismatches |
| `code-reviewer` | Reviews changed C# and Python files for correctness, conventions, and security issues |

## Hooks

| Hook | Trigger | Action |
|------|---------|--------|
| Pre-edit | Any file edit | Scans new content for hardcoded credentials; blocks if found |
| Post-edit | Any file edit | Runs `py_compile` on `.py` files; runs `dotnet build` on `.cs` files |

## Conventions

- **C#**: sealed classes, record DTOs, `required` modifier on non-nullable strings
- **Python**: `logging` for all output (never `print`), type hints on all functions
- **Secrets**: never hardcoded — always `.env` or `appsettings.Development.json`
- **Commits**: one logical layer per commit; no auto-push
