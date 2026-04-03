# Real Example: Before vs After MCP

This folder shows how an LLM works with **Google Search** and **Database** in two different ways.

**Both scripts now use the REAL OpenAI API.**

## Files

| File | Purpose |
|------|---------|
| `demo_db_setup.py` | Creates a practice SQLite database |
| `before_mcp_real.py` | OLD WAY: custom code, manual tool calling |
| `after_mcp_real.py` | NEW WAY: FastMCP, standard protocol |
| `.env.example` | Example API key file |

## Setup

### Step 1: Get your OpenAI API key
Go to [OpenAI Platform](https://platform.openai.com/) and get your API key.

### Step 2: Create `.env` file
```bash
cp .env.example .env
```
Then edit `.env` and paste your real key:
```
OPENAI_API_KEY=sk-your_openai_api_key_here
```

### Step 3: Create the demo database
```bash
python demo_db_setup.py
```

## How to run

### Run the OLD WAY
```bash
python before_mcp_real.py
```

### Run the NEW WAY
```bash
python after_mcp_real.py
```

## What you will learn

- **Before MCP:** The developer manually writes tool definitions in Python, manually maps tool names to functions, and glues everything together. Adding a new tool means editing code by hand.
- **After MCP:** Tools are registered with `@mcp.tool()`. OpenAI discovers them automatically from the MCP server and calls them through the standard protocol.
