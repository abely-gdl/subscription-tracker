# Subscription Tracker

Full-stack subscription management system — .NET 9 Minimal API + Python MCP Server + Claude Code integration.

## Architecture

```
Claude Code → MCP Server (Python) → .NET 9 API → SQLite
```

## Prerequisites

- .NET 9 SDK
- Python 3.11+

## Setup

### 1. Configure secrets

Both the API and the MCP server need the same API key. The `.example` files are templates — copy them and fill in your real values.

**Windows (CMD):**
```cmd
copy backend\SubscriptionTracker.Api\appsettings.Development.json.example ^
     backend\SubscriptionTracker.Api\appsettings.Development.json

copy mcp-server\.env.example mcp-server\.env
```

**Windows (PowerShell):**
```powershell
Copy-Item backend\SubscriptionTracker.Api\appsettings.Development.json.example `
          backend\SubscriptionTracker.Api\appsettings.Development.json

Copy-Item mcp-server\.env.example mcp-server\.env
```

Then open both files and set the same API key value in each:
- `appsettings.Development.json` → set `"ApiKey": "choose-any-secret-value"`
- `mcp-server\.env` → set `API_KEY=choose-any-secret-value`

### 2. Start the API

```cmd
cd backend\SubscriptionTracker.Api
dotnet run
```

Listens on `http://localhost:5000`. The SQLite database (`subscriptions.db`) is created automatically on first run.

### 3. Set up the MCP server Python environment (one-time)

```cmd
cd mcp-server
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 4. Open in Claude Code

Open this folder in Claude Code. The MCP server starts automatically via `.claude/settings.json`.

---

## API Endpoints

All endpoints require `X-Api-Key: <your-key>` header, except `/health`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth) |
| GET | `/subscriptions` | List all |
| GET | `/subscriptions/{id}` | Get one |
| GET | `/subscriptions/category/{cat}` | Filter by category |
| POST | `/subscriptions` | Create |
| PUT | `/subscriptions/{id}` | Update |
| DELETE | `/subscriptions/{id}` | Delete |

### Test with curl

```cmd
curl http://localhost:5000/health

curl http://localhost:5000/subscriptions -H "X-Api-Key: dev-secret-key-change-me"

curl -X POST http://localhost:5000/subscriptions ^
  -H "X-Api-Key: dev-secret-key-change-me" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Netflix\",\"cost\":15.99,\"billingCycle\":\"Monthly\",\"category\":\"Streaming\",\"renewalDate\":\"2026-05-15\",\"status\":\"Active\"}"
```

Or open `http-tests\subscriptions.http` in VS Code with the REST Client extension.

---

## MCP Inspector

Verify all tools, resources, and prompts from the project root:

```cmd
npx @modelcontextprotocol/inspector mcp-server\.venv\Scripts\python mcp-server\server.py
```

Opens a browser UI at `http://localhost:5173`. Test each tool manually and check resources return JSON and prompts return text.

---

## Claude Code Skills

| Command | Description |
|---------|-------------|
| `/cost-report` | Spending breakdown by category and billing period |
| `/spending-forecast` | 12-month cost projection |

Type the command directly in the Claude Code prompt:

```
/cost-report
```

```
/spending-forecast
```

---

## Sub-agents

| Agent | Description |
|-------|-------------|
| `api-contract-checker` | Checks MCP tool definitions stay in sync with .NET API endpoints |
| `code-reviewer` | Reviews changed C# and Python files for correctness, conventions, and security |

Trigger by asking Claude naturally — no special syntax needed:

```
Check if the MCP tools are in sync with the API
```

```
I changed the Subscription model — verify nothing is broken between the API and MCP server
```

```
Review my recent changes before I commit
```

```
Do a code review of the endpoints file
```

---

## Hooks

Hooks run automatically on every file edit — no manual trigger needed.

**Pre-edit hook** (secrets check): ask Claude to hardcode a secret in any file.
```
Add api_key = "my-real-secret-123" to server.py
```
Expected: Claude Code blocks the edit and prints a secret-detected warning.

**Post-edit hook** (build check): edit any `.py` or `.cs` file.
- `.py` → runs `python -m py_compile` and surfaces any syntax errors
- `.cs` → runs `dotnet build backend/SubscriptionTracker.Api` and surfaces any compilation errors

To test the .cs build check, ask Claude to introduce a syntax error:
```
Add a broken line to Subscription.cs
```
Expected: Claude Code shows a dotnet build failure immediately after the edit.
