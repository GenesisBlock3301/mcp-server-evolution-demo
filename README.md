# MCP Server Evaluation: A Beginner's Guide

*A simple guide to understanding how AI agents use tools, and why the Model Context Protocol (MCP) changed everything.*

---

## Table of Contents

1. [What is the Problem? (Before MCP)](#1-what-is-the-problem-before-mcp)
2. [What is MCP? (After MCP)](#2-what-is-mcp-after-mcp)
3. [How Are AI Agents Graded?](#3-how-are-ai-agents-graded)
4. [Common Failure Patterns](#4-common-failure-patterns)
5. [Why Do AIs Guess Wrong or Get Stuck?](#5-why-do-ais-guess-wrong-or-get-stuck)
6. [MCP vs HTTP](#6-mcp-vs-http)
7. [How Server, Tools, and Client Connect](#7-how-server-tools-and-client-connect)
8. [Code Examples](#8-code-examples)
9. [Quick Checklist](#9-quick-checklist)
10. [What to Learn Next](#10-what-to-learn-next)

---

## 1. What is the Problem? (Before MCP)

AI agents need tools to do real work:
- Read files from your computer
- Search the web
- Query a database

But before MCP, every tool had **different rules**. There was no common language. This caused four serious problems:

| Problem | What it means |
|---------|---------------|
| **No shared rules** | Every tool used a different API format. The AI had to learn new rules for every tool. |
| **Fake checking** | Testers only read the AI's text answer. They did not check if the job was really done. |
| **No fair comparison** | You could not compare two AI agents fairly because each test used different tools and rules. |
| **No cost tracking** | Nobody carefully tracked how much money or time the AI wasted. |

> **In short:** Before MCP, there was no common plug. Every tool had its own socket.

---

## 2. What is MCP? (After MCP)

**MCP = Model Context Protocol**

Think of MCP as a **USB-C cable** for AI tools.
- Before: Every phone had a different charger.
- After: One cable fits many phones.

MCP creates **one rulebook** that all tools can follow.

### What changed?

| Question | Before MCP | After MCP |
|----------|------------|-----------|
| Do all tools use the same rules? | No | **Yes** |
| Do testers check real results? | Usually no | **Yes** |
| Can AI use many tools together? | Rarely tested | **Yes, standard practice** |
| Do they track money and time? | Not really | **Yes** |
| Are failures explained clearly? | Only "pass" or "fail" | **Detailed error types** |

> **In short:** After MCP, we use one rulebook and check real results.

---

## 3. How Are AI Agents Graded?

Testers ask **three basic questions** when they evaluate an MCP agent:

### 1. Did it finish the job?
- Did the AI complete the full task?
- Is the final result actually correct?

### 2. Did it pick the right tools?
- Did it choose the correct tools?
- Did it use them in the right order?
- Did it pass the correct arguments and settings?

### 3. Was it cheap and fast?
- **Token cost:** Did it use too many words (tokens) in the conversation?
- **Time cost:** Did it take too long to finish?
- **Money cost:** Did it waste API call budget?

All other metrics are just details of these three questions.

---

## 4. Common Failure Patterns

When MCP agents fail, they usually fail in one of three ways:

| Failure type | What happened | Example |
|--------------|---------------|---------|
| **Wrong content** | The AI created something, but the data inside was broken. | It wrote a CSV file, but some emails were missing or spelled wrong. |
| **Stuck halfway** | The AI started the task but could not finish one hard step. | It logged into a website but got stuck on a "robot check." |
| **Forgot the last part** | The AI did 90% of the work but missed the final step. | It created a database table and columns but forgot to insert the required rows. |

---

## 5. Why Do AIs Guess Wrong or Get Stuck?

In our code demo, you saw OpenAI sometimes guess the wrong database table or column. Here is why that happens:

### The AI Cannot See Your Computer
The AI lives in the cloud. It cannot see your real files, tables, or websites. It only reads **text descriptions** that you give it. If your description is vague, the AI will **guess**.

**Example:** In our demo, OpenAI guessed a table called `smartphones`, but the real table was `products`. It also guessed a `category` column that did not exist.

**Fix:** Write very clear tool descriptions. Mention exact table names, column names, and data formats.

### The AI Thinks One Step at a Time
In each turn, the AI only decides the **next action**. It does not plan the whole journey at the start. This means it can:
- Forget the original goal
- Stop early, thinking it is already done
- Try wrong SQL queries and need several turns to fix itself

### The AI Is Slightly Random
Even with the same question, the AI might answer differently each time. This is controlled by **temperature**. Higher temperature = more creativity and randomness. Lower temperature = more repetition and predictability.

### The AI Cannot Tell Error vs. Empty Result
Look at these two outputs:

| Output | Meaning | Will AI retry? |
|--------|---------|----------------|
| `DB error: no such column: rating` | The SQL was wrong | **Yes** |
| `DB result: []` | The SQL worked, but nothing matched | **No** |

When the AI sees an **error**, it knows it made a mistake and tries again. When it sees `[]` (empty list), it thinks "zero results found" and stops. In our demo, OpenAI searched `WHERE name LIKE '%smartphone%'`, got `[]`, and gave up — even though `iPhone 15` is a smartphone.

---

## 6. MCP vs HTTP

**MCP and HTTP are not the same thing.**

### HTTP
HTTP = HyperText Transfer Protocol. It is the general language of the web. Your browser uses it to load websites. APIs use it to send data. It carries anything: web pages, images, videos, JSON data.

### MCP
MCP = Model Context Protocol. It is **specialized for AI agents**. It defines:
- How tools are described
- How an AI asks: "What tools do you have?"
- How an AI says: "Call tool X with arguments Y"
- How results are sent back in a standard format

### Relationship
**MCP can run on top of HTTP**, but it can also run on other transports. Think of it like this:

| Protocol | Analogy |
|----------|---------|
| **HTTP** | A **public road**. Any vehicle can use it. |
| **MCP** | A **delivery contract**. It defines how packages must be labeled, tracked, and delivered. The truck can drive on the road (HTTP) or move through a private hallway (`stdio`). |

In our `real_example/` code, we use **`stdio`** (standard input/output) instead of HTTP. The MCP server runs as a small program on the same computer, and the client talks to it through text pipes. We chose `stdio` because it is simpler — no ports, no network setup, no firewall issues.

> **Summary:** HTTP is a road. MCP is a set of traffic rules for AI agents.

---

## 7. How Server, Tools, and Client Connect

This is the most confusing part for beginners. Here is the exact flow in our `real_example/after_mcp_real.py` code.

### Step 1: Create the server object
```python
mcp = FastMCP("SmartphoneHelper")
```
This builds a server container. It is empty at first.

### Step 2: Register tools
```python
@mcp.tool()
def google_search(query: str) -> str:
    ...
```
This adds a tool to the server's internal registry. The `mcp` object now remembers `google_search`.

### Step 3: Start the server
```python
mcp.run(transport='stdio')
```
This starts the server as a live process. It listens for JSON messages on standard input and replies on standard output.

### Step 4: The client connects
```python
async with stdio_client(server) as (read, write):
    async with ClientSession(read, write) as session:
        tools_response = await session.list_tools()
```
The client opens a connection and asks the server: **"What tools do you have?"**

### Step 5: The server replies
The server reads its internal registry (all functions decorated with `@mcp.tool()`) and returns the list. Then the client can call any tool through the standard protocol.

### Visual diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR PYTHON SCRIPT                       │
│  ┌──────────────────┐          ┌──────────────────┐         │
│  │   OpenAI Client  │          │   MCP Client     │         │
│  │  ( decides what  │◄────────►│  ( talks to the  │         │
│  │   to do next )   │          │    server )      │         │
│  └──────────────────┘          └────────┬─────────┘         │
└─────────────────────────────────────────┼───────────────────┘
                                          │
                                          │ stdio pipe
                                          │ (text messages)
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP SERVER PROCESS                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              mcp = FastMCP("...")                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐   │   │
│  │  │ @mcp.tool()  │  │ @mcp.tool()  │  │   ...     │   │   │
│  │  │ google_search│  │   query_db   │  │  (more)   │   │   │
│  │  └──────────────┘  └──────────────┘  └───────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Message flow example

```
Step 1: Client asks for the menu
         ┌────────┐                 ┌────────┐
         │ Client │ ── list_tools() ─►│ Server │
         └────────┘                 └────────┘
                                          │
                                          ▼
                                    Reads @mcp.tool() registry

Step 2: Server replies with tools
         ┌────────┐                 ┌────────┐
         │ Client │ ◄── {google_search, query_db} ─│ Server │
         └────────┘                 └────────┘

Step 3: Client asks to run a tool
         ┌────────┐                 ┌────────┐
         │ Client │ ── call_tool("query_db") ─►│ Server │
         └────────┘                 └────────┘
                                          │
                                          ▼
                                    Runs Python function

Step 4: Server sends back result
         ┌────────┐                 ┌────────┐
         │ Client │ ◄── "DB result: [...]" ─│ Server │
         └────────┘                 └────────┘
```

**Key point:** `@mcp.tool()` only registers the tool inside the `mcp` object. Nothing happens until `mcp.run()` starts the server, and `stdio_client` connects to it. The decorator, the server, and the client are three links in one chain.

---

## 8. Code Examples

You can find working code in the `real_example/` folder:

| File | What it shows |
|------|---------------|
| `before_mcp_real.py` | The old way: manual tool definitions, manual routing, hardcoded JSON schemas. |
| `after_mcp_real.py` | The new way: FastMCP server, automatic tool discovery, standard protocol calls. |
| `demo_db_setup.py` | Creates a simple SQLite database for testing. |

Run `before_mcp_real.py` and `after_mcp_real.py` side by side to feel the difference.

---

## 9. Quick Checklist

When you test or build an MCP agent, ask these six questions:

1. **Does it follow the MCP rules?**
2. **Did it really do the task, or only talk about it?**
3. **Can it use 2 or 3 tools together?**
4. **If it fails, do you know exactly why?**
5. **Was it fast and cheap?**
6. **Does the task feel like a real human job?**

---

## 10. What to Learn Next

- How to add a third tool to the demo
- GitHub and Notion MCP real-world examples
- How to read MCP benchmark papers
- How to deploy an MCP server over HTTP for remote use
