# LMS Telegram Bot — Development Plan

## Overview

This document describes the implementation plan for the LMS Telegram Bot across four tasks. The bot provides students with access to their learning management system data (labs, scores, analytics) through Telegram, and eventually through natural language queries powered by an LLM.

## Architecture Principles

### Separation of Concerns

The core architectural decision is to separate **handlers** (command logic) from **transport** (Telegram API). Handlers are pure functions that take input and return text. They don't know about Telegram. This enables:

- **Test mode**: Call handlers directly via CLI without Telegram connection
- **Unit testing**: Test handler logic in isolation
- **Future flexibility**: Swap Telegram for another messenger without rewriting handlers

### Configuration Management

All secrets (tokens, API keys) are loaded from `.env.bot.secret` using `pydantic-settings`. This pattern:
- Keeps secrets out of version control (`.env.bot.secret` is gitignored)
- Provides type-safe configuration with validation
- Uses `.env.bot.example` as a template for required variables

### API Client Pattern

External services (LMS API, LLM API) are accessed through dedicated client classes in `bot/services/`. Each client:
- Handles authentication (Bearer tokens)
- Manages HTTP connections and timeouts
- Transforms raw API responses into structured data
- Gracefully handles network errors

---

## Task 1: Scaffold and Plan

**Goal:** Create project structure with testable handler architecture.

**Deliverables:**
- `bot/bot.py` — Entry point with `--test` mode
- `bot/handlers/` — Command handlers (start, help, health, labs, scores)
- `bot/services/` — API client layer (LMS API client stub)
- `bot/config.py` — Configuration loader
- `bot/pyproject.toml` — Dependencies
- `bot/PLAN.md` — This document

**Acceptance:**
- `cd bot && uv run bot.py --test "/start"` prints welcome message
- All handlers return placeholder text without crashing
- Exit code 0 for all test commands

---

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Changes:**
- Implement `LmsApiClient` in `bot/services/lms_api.py`
- Update `/health` handler to check actual backend status
- Update `/labs` handler to fetch real items from `/items/`
- Update `/scores` handler to query `/analytics/scores?lab=lab-XX`
- Add error handling for network failures and API errors

**Handler Pattern:**
```python
def handle_health() -> str:
    client = LmsApiClient(settings.lms_api_base_url, settings.lms_api_key)
    if client.health_check():
        return "✅ Backend: OK"
    return "❌ Backend: Unreachable"
```

**Acceptance:**
- `/health` returns real backend status
- `/labs` shows actual labs from the database
- `/scores lab-04` shows score distribution
- Graceful error messages when API is down

---

## Task 3: LLM Intent Routing

**Goal:** Enable natural language queries via LLM tool calling.

**Architecture:**
The LLM acts as an **intent router**. Instead of parsing commands with regex, we describe tools to the LLM and let it decide which to call.

**Tool Descriptions:**
```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get student scores for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}
                },
                "required": ["lab"]
            }
        }
    },
    # ... more tools
]
```

**System Prompt:**
```
You are an assistant for a learning management system.
Use the available tools to answer student questions.
If a tool doesn't exist for the query, say you can't help.
```

**Flow:**
1. User: "what did I get on lab 4?"
2. LLM → calls `get_scores(lab="lab-04")`
3. Bot executes tool, gets result
4. Bot sends result to user

**Acceptance:**
- Plain text queries route to correct handlers
- LLM extracts parameters (lab numbers, student IDs)
- Fallback message when intent is unclear

---

## Task 4: Docker Deployment

**Goal:** Containerize the bot for production deployment.

**Dockerfile Structure:**
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY bot/ /app/bot/
COPY pyproject.toml uv.lock /app/
RUN pip install uv && uv sync --locked
CMD ["python", "-m", "bot.bot"]
```

**Docker Compose:**
Add bot service to existing `docker-compose.yml`:
```yaml
bot:
  build:
    context: .
    dockerfile: bot/Dockerfile
  env_file:
    - .env.bot.secret
  depends_on:
    - backend
  networks:
    - lms-network
```

**Networking:**
- Bot uses service name `backend` (not `localhost`) to reach API
- `LMS_API_BASE_URL=http://backend:8000` inside container
- External callers use `http://localhost:42002` (caddy proxy)

**Acceptance:**
- `docker compose up --build` starts bot
- Bot responds in Telegram
- Bot restarts on failure (`restart: unless-stopped`)

---

## Testing Strategy

### Test Mode (CLI)
```bash
uv run bot.py --test "/start"
uv run bot.py --test "/scores lab-04"
```

### Unit Tests (future)
```python
def test_handle_scores():
    result = handle_scores(lab="lab-04")
    assert "lab-04" in result
```

### Integration Tests (future)
```python
def test_lms_api_client():
    client = LmsApiClient(url, key)
    assert client.health_check() is True
```

---

## File Structure

```
bot/
├── bot.py              # Entry point (--test + Telegram)
├── config.py           # Settings loader
├── pyproject.toml      # Dependencies
├── PLAN.md             # This file
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   ├── help.py
│   ├── health.py
│   ├── labs.py
│   └── scores.py
└── services/
    ├── __init__.py
    ├── lms_api.py      # LMS API client
    └── llm_api.py      # LLM client (Task 3)
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM picks wrong tool | Improve tool descriptions, not regex fallbacks |
| API returns unexpected data | Defensive parsing with try/except |
| Bot crashes in production | Docker restart policy, logging |
| Secrets committed to git | `.env.bot.secret` in `.gitignore`, use example file |

---

## Future Enhancements (Out of Scope)

- Inline keyboards for lab selection
- Subscription to score updates (push notifications)
- Multi-language support
- Admin commands for instructors
