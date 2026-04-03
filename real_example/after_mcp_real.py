# after_mcp_real.py
# This shows the NEW WAY: LLM + Google Search + DB with FastMCP.

import os
import sys
import sqlite3
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import FastMCP
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import json

load_dotenv()

# --- Setup ---
DB_PATH = "demo.db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not found. Add it to .env")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# --- STEP 1: Define the MCP server and tools ---
mcp = FastMCP("SmartphoneHelper")


@mcp.tool()
def google_search(query: str) -> str:
    """Search the web for information."""
    print(f"  [Tool] google_search: {query}", file=sys.stderr, flush=True)
    return (
        f"Search results for '{query}':\n"
        "1. iPhone 15 has excellent camera and battery life.\n"
        "2. Samsung Galaxy S24 has great AI features.\n"
        "3. Google Pixel 8 is best for pure Android experience.\n"
    )


@mcp.tool()
def query_db(sql: str) -> str:
    """
    Run a SQL query on the local SQLite database.
    Table 'products' has columns: id, name, price, stock.
    """
    print(f"  [Tool] query_db: {sql}", file=sys.stderr, flush=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return f"DB result: {rows}"
    except Exception as e:
        conn.close()
        return f"DB error: {e}"


# --- Helper: Convert MCP tools to OpenAI format ---
def to_openai_tools(mcp_tools):
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            }
        }
        for tool in mcp_tools
    ]


# --- STEP 2: Main logic ---
async def main():
    print("=== AFTER MCP: FastMCP + OpenAI ===\n")

    question = "What is the best smartphone to buy? Check the web and our database."
    print(f"User asks: {question}\n")

    # Start the MCP server as a child process and connect to it
    # We use sys.executable to make sure we use the SAME Python interpreter.
    # We also pass env to avoid PyCharm debugger injection into the subprocess.
    server = StdioServerParameters(
        command=sys.executable,
        args=["-u", "-c", "from after_mcp_real import mcp; mcp.run(transport='stdio')"],
        env={
            **os.environ,
            "PYTHONIOENCODING": "utf-8",
            # This tells PyCharm not to attach its debugger to the subprocess:
            "PYDEVD_USE_FRAME_EVAL": "NO",
            "PYDEVD_DISABLE_FILE_VALIDATION": "1",
        },
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools automatically from the MCP server
            tools_response = await session.list_tools()
            tools = to_openai_tools(tools_response.tools)

            print(f"OpenAI discovered {len(tools)} tools:")
            for t in tools:
                print(f"  - {t['function']['name']}")
            print()

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use available tools, then answer."
                },
                {"role": "user", "content": question}
            ]

            MAX_TURNS = 5
            for turn in range(MAX_TURNS):
                print(f"--- Turn {turn + 1} ---")

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=tools,
                    temperature=0.3,
                )
                message = response.choices[0].message

                if message.tool_calls:
                    # Record OpenAI's tool request
                    messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    })

                    # Run each tool through MCP and record results
                    for tc in message.tool_calls:
                        name = tc.function.name
                        args = json.loads(tc.function.arguments)
                        print(f"OpenAI wants to call: {name}({args})")

                        result = await session.call_tool(name, arguments=args)
                        answer = result.content[0].text
                        print(f"Tool result: {answer[:80]}...")

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": answer
                        })
                else:
                    print(f"\nFinal answer: {message.content}")
                    break

    print("\n=== WHY THIS IS BETTER ===")
    print("1. @mcp.tool() - one standard rule.")
    print("2. OpenAI discovers tools automatically.")
    print("3. session.call_tool() - same interface for all tools.")
    print("4. No manual TOOL_MAP needed.")
    print("5. Other projects can reuse this server easily.")


if __name__ == "__main__":
    asyncio.run(main())
