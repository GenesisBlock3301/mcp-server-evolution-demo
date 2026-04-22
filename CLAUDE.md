# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This is an educational demo repository that shows the evolution of AI agent tool integration — from ad-hoc custom glue code ("before MCP") to the standardized Model Context Protocol ("after MCP"). It is structured in three layers of increasing complexity.

## Repository Layout

| Directory | What it demonstrates |
|-----------|---------------------|
| `mock_code/` | Pure-Python conceptual demo — no real APIs, no dependencies |
| `real_example/` | Real OpenAI API calls; `stdio` transport; single-client MCP |
| `fastAPI/` | Production-style server; HTTP/SSE transport; multi-client MCP |
| `contacts/` | Sample `.txt` data files consumed by the `mock_code/` demos |
| `hugging_face/` | Reserved for future Hugging Face examples |

## Running the Code

### mock_code (no setup needed)

```bash
cd mock_code
python before_mcp.py   # shows custom per-agent approaches + fake evaluators
python after_mcp.py    # shows shared FilesystemMCP tool + fair evaluator
```

### real_example (requires OPENAI_API_KEY in `.env`)

```bash
cd real_example
python demo_db_setup.py     # creates demo.db with 4 products
python before_mcp_real.py   # manual TOOLS list + TOOL_MAP approach
python after_mcp_real.py    # FastMCP server over stdio + auto tool discovery
```

`after_mcp_real.py` spawns the MCP server as a subprocess via `StdioServerParameters`. The server is imported from the same file (`from after_mcp_real import mcp`), so both client and server live in one file.

### fastAPI (multi-client, HTTP/SSE)

```bash
cd fastAPI
pip install -r requirements.txt
python main.py                                         # starts on port 8000
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

python seed_tasks.py   # optional: insert 100 sample tasks

curl http://localhost:8000/health
curl -N http://localhost:8000/mcp/sse   # verify MCP SSE endpoint

docker-compose up -d   # production: FastAPI + Nginx reverse proxy
```

## Architecture

### Transport comparison

| Transport | Used in | Clients | Lifetime |
|-----------|---------|---------|----------|
| `stdio` | `real_example/` | 1 (subprocess) | Lives only while parent script runs |
| HTTP/SSE | `fastAPI/` | Many | Always-on, independent process |

### fastAPI internals

`main.py` creates a `FastAPI` app and mounts the FastMCP server at `/mcp` via SSE:

```python
mcp_app = mcp.http_app(transport="sse")
app.mount("/mcp", mcp_app)
```

`mcp_server.py` defines all 16+ tools with `@mcp.tool()`. Tools return JSON strings (not Pydantic models) because MCP tool results are plain text.

`database.py` exposes a `get_db()` context manager that sets `row_factory = sqlite3.Row` so rows can be accessed as dicts.

`models.py` contains Pydantic models used only by the REST endpoints (`/api/tasks`, `/api/notes`) — not by the MCP tools.

### Database schemas

**`real_example/demo.db`** — `products(id, name, price, stock)`

**`fastAPI/tasks_notes.db`** — two tables:
- `tasks(id, title, description, priority, status, due_date, created_at, completed_at)`
- `notes(id, title, content, tags, created_at, updated_at)`

## Environment

Requires `OPENAI_API_KEY` in a `.env` file at the repo root (used only by `real_example/`):

```
OPENAI_API_KEY=sk-...
```

`.env` must never be committed. The `fastAPI/` server has no API key dependency.

## Key Patterns

- All MCP tools use `@mcp.tool()` decorator — the docstring becomes the tool description sent to the LLM, so it must be precise about table/column names and argument formats.
- `real_example/after_mcp_real.py` passes `env={**os.environ, "PYDEVD_USE_FRAME_EVAL": "NO"}` to the subprocess to prevent PyCharm debugger injection.
- `update_task` / `update_note` in `mcp_server.py` build SQL `SET` clauses dynamically from non-empty arguments — passing an empty string means "no change", not "clear the field".