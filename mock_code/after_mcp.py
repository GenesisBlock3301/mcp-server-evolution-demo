# after_mcp.py
# This script shows the NEW WAY (after MCP) for the same file task.
# Now there is ONE common rulebook and ONE fair evaluator.

import os
import csv
import re
import shutil

# ---------------------------------------------------------------------------
# STEP 1: Make fake data (same as before)
# ---------------------------------------------------------------------------
def setup_contacts_folder():
    """Make a folder with 2 contact files."""
    if os.path.exists("contacts"):
        shutil.rmtree("contacts")
    os.makedirs("contacts", exist_ok=True)
    with open("contacts/alice.txt", "w") as f:
        f.write("Name: Alice\nEmail: alice@example.com\n")
    with open("contacts/bob.txt", "w") as f:
        f.write("Name: Bob\nEmail: bob@test.com\n")
    # Clean old result
    if os.path.exists("emails.csv"):
        os.remove("emails.csv")


# ---------------------------------------------------------------------------
# STEP 2: The MCP Tool (one common rulebook)
# ---------------------------------------------------------------------------
class FilesystemMCP:
    """
    This is the STANDARD tool. Both agents MUST use this.
    No more secret custom ways.
    """
    def list_files(self, folder_path):
        return os.listdir(folder_path)

    def read_file(self, file_path):
        with open(file_path) as f:
            return f.read()

    def write_csv(self, file_path, rows):
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for row in rows:
                writer.writerow(row)


# ---------------------------------------------------------------------------
# STEP 3: Two AI agents use the SAME tool
# ---------------------------------------------------------------------------

def agent_1_with_mcp(tool):
    """
    Agent 1 now uses the standard MCP tool.
    It does the job correctly.
    """
    files = tool.list_files("contacts")
    emails = []
    for fname in files:
        content = tool.read_file(f"contacts/{fname}")
        match = re.search(r"Email: (.+)", content)
        if match:
            emails.append(match.group(1))
    
    rows = [["email"]] + [[email] for email in emails]
    tool.write_csv("emails.csv", rows)
    return "Task done using MCP tool"


def agent_2_with_mcp(tool):
    """
    Agent 2 also uses the standard MCP tool.
    But it still has the same old bug: it skips bob.txt.
    """
    files = tool.list_files("contacts")
    emails = []
    for fname in files:
        if fname == "bob.txt":
            continue  # Same bug as before
        content = tool.read_file(f"contacts/{fname}")
        match = re.search(r"Email: (.+)", content)
        if match:
            emails.append(match.group(1))
    
    rows = [["email"]] + [[email] for email in emails]
    tool.write_csv("emails.csv", rows)
    return "Task done using MCP tool"


# ---------------------------------------------------------------------------
# STEP 4: ONE fair evaluator (checks real results)
# ---------------------------------------------------------------------------

def mcp_evaluator():
    """
    After MCP: There is ONE evaluator for everyone.
    It does NOT care what text the agent said.
    It only checks the REAL file on the computer.
    """
    # Check 1: Does the file exist?
    if not os.path.exists("emails.csv"):
        return "FAIL - emails.csv was not created"
    
    # Check 2: Is the content correct?
    with open("emails.csv") as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if rows != [["email"], ["alice@example.com"], ["bob@test.com"]]:
        return "FAIL - emails.csv is missing data or has wrong content"
    
    return "PASS"


# ---------------------------------------------------------------------------
# STEP 5: Run everything and show the fix
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    setup_contacts_folder()
    print("=== AFTER MCP: One common rulebook ===\n")

    tool = FilesystemMCP()

    # Run Agent 1
    print("Agent 1 result:")
    agent_1_with_mcp(tool)
    print(f"  Evaluator says: {mcp_evaluator()}")
    print("  The evaluator checked the REAL file. It is correct.\n")

    # Clean up for Agent 2
    if os.path.exists("emails.csv"):
        os.remove("emails.csv")

    # Run Agent 2
    print("Agent 2 result:")
    agent_2_with_mcp(tool)
    print(f"  Evaluator says: {mcp_evaluator()}")
    print("  The evaluator checked the REAL file. Bob is missing!")
    print("  So Agent 2 gets FAIL. No more fake passes.\n")

    # Summary
    print("=== THE FIX ===")
    print("1. Both agents use the SAME standard tool (FilesystemMCP).")
    print("2. One evaluator checks the SAME real result for both agents.")
    print("3. Agent 1 passes because the file is really correct.")
    print("4. Agent 2 fails because the file is really broken.")
    print("5. Now we can FAIRLY compare them!")
