# before_mcp_real.py
# This shows the OLD WAY: LLM + Google Search + DB without MCP.
# Everything is glued together manually with custom code.
# NOW USING REAL OPENAI API.

import os
import sqlite3
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DB_PATH = "demo.db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not found.")
    print("Please set your OpenAI API key in the .env file:")
    print("  OPENAI_API_KEY=your_key_here")
    exit(1)

client = OpenAI(
    api_key=OPENAI_API_KEY,
)

# ---------------------------------------------------------------------------
# STEP 1: Custom tools (no standard rules)
# ---------------------------------------------------------------------------

def google_search(query: str) -> str:
    """
    MOCK Google Search.
    In real life, you would call Google API or SerpAPI here.
    """
    print(f"  [Tool] google_search called with: {query}")
    return (
        f"Search results for '{query}':\n"
        "1. iPhone 15 has excellent camera and battery life.\n"
        "2. Samsung Galaxy S24 has great AI features.\n"
        "3. Google Pixel 8 is best for pure Android experience.\n"
    )


def query_db(sql: str) -> str:
    """
    Custom DB query function.
    """
    print(f"  [Tool] query_db called with: {sql}")
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


# We need a map so we can call the right function when OpenAI asks for a tool
TOOL_MAP = {
    "google_search": google_search,
    "query_db": query_db,
}


# ---------------------------------------------------------------------------
# STEP 2: Define tools for OpenAI (OpenAI format)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "google_search",
            "description": "Search the web for information about smartphones or any topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_db",
            "description": "Run a SQL query on the local SQLite database. The database has one table called 'products' with columns: id, name, price, stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["sql"]
            }
        }
    }
]


# ---------------------------------------------------------------------------
# STEP 3: The main flow (manual glue code + real OpenAI)
# ---------------------------------------------------------------------------

def main():
    print("=== BEFORE MCP: Custom integration with REAL OpenAI API ===\n")

    question = "What is the best smartphone to buy? Check the web and our database."
    print(f"User asks: {question}\n")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. You have access to two tools: "
                "google_search and query_db. "
                "Use the tools to gather information, then give a final answer."
            )
        },
        {"role": "user", "content": question}
    ]

    # We MUST use a loop because tool calling is a multi-turn conversation.
    # Turn 1: OpenAI asks for a tool -> we run it -> send result back
    # Turn 2: OpenAI asks for another tool -> we run it -> send result back
    # Turn N: OpenAI gives final answer -> we stop
    # range(5) is a safety seatbelt. If OpenAI goes into an infinite loop,
    # we force-stop after 5 turns. Increase this if your agent uses more tools.
    MAX_TURNS = 5
    for turn in range(MAX_TURNS):
        print(f"--- Turn {turn + 1} ---")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            temperature=0.3,
        )

        message = response.choices[0].message

        # If OpenAI wants to use a tool
        if message.tool_calls:
            # Append assistant's tool request to history
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

            # Execute each tool call
            for tc in message.tool_calls:
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments)
                print(f"OpenAI wants to call: {tool_name}({tool_args})")

                if tool_name in TOOL_MAP:
                    result = TOOL_MAP[tool_name](**tool_args)
                else:
                    result = f"Error: unknown tool {tool_name}"

                # IMPORTANT: Every tool call has a unique ID (tc.id).
                # Even if OpenAI calls the same tool 3 times, each call gets a different ID.
                # We MUST send the result back with the matching ID so OpenAI knows
                # which answer belongs to which question.
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        else:
            # Final answer
            print(f"\nFinal answer: {message.content}")
            break

    print("\n=== THE PROBLEM ===")
    print("1. The developer manually wrote the TOOLS list in Python code.")
    print("2. The developer manually mapped tool names to Python functions (TOOL_MAP).")
    print("3. If you add a new tool, you must edit TOOLS and TOOL_MAP by hand.")
    print("4. Another project cannot reuse this without copying all the custom glue.")


if __name__ == "__main__":
    main()
