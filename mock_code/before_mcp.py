# before_mcp.py
# This script shows the OLD WAY (before MCP) for a simple file task.
# We use simple English and simple code.

import os
import csv
import re

# ---------------------------------------------------------------------------
# STEP 1: Make fake data
# ---------------------------------------------------------------------------
def setup_contacts_folder():
    """Make a folder with 2 contact files."""
    os.makedirs("contacts", exist_ok=True)
    with open("contacts/alice.txt", "w") as f:
        f.write("Name: Alice\nEmail: alice@example.com\n")
    with open("contacts/bob.txt", "w") as f:
        f.write("Name: Bob\nEmail: bob@test.com\n")


# ---------------------------------------------------------------------------
# STEP 2: Two AI agents do the same job in DIFFERENT ways
# ---------------------------------------------------------------------------

def agent_1_custom_approach():
    """
    Agent 1 does the job in its own special way.
    It reads files and only returns a text sentence.
    It does NOT make emails.csv.
    """
    files = os.listdir("contacts")
    emails = []
    for fname in files:
        with open(f"contacts/{fname}") as f:
            content = f.read()
            match = re.search(r"Email: (.+)", content)
            if match:
                emails.append(match.group(1))
    return f"I found these emails: {', '.join(emails)}"


def agent_2_custom_approach():
    """
    Agent 2 does the job in a DIFFERENT special way.
    It makes emails.csv but forgets to add Bob's email.
    """
    files = os.listdir("contacts")
    with open("emails.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["email"])
        for fname in files:
            # Oops! Agent 2 has a bug: it only reads .txt files... wait, that is okay.
            # But wait, it skips bob.txt by mistake because of a silly bug.
            if fname == "bob.txt":
                continue  # Bug: forgot Bob!
            with open(f"contacts/{fname}") as f:
                content = f.read()
                match = re.search(r"Email: (.+)", content)
                if match:
                    writer.writerow([match.group(1)])
    return "emails.csv created successfully"


# ---------------------------------------------------------------------------
# STEP 3: Evaluators also work in DIFFERENT ways
# ---------------------------------------------------------------------------

def evaluator_for_agent_1(result_text):
    """
    Before MCP: Evaluator only reads the agent's text answer.
    It does NOT check if emails.csv was really made.
    """
    if "alice@example.com" in result_text and "bob@test.com" in result_text:
        return "PASS"
    return "FAIL"


def evaluator_for_agent_2(result_text):
    """
    Before MCP: Another evaluator only checks for a success sentence.
    It does NOT open the CSV file to check if the data is correct.
    """
    if "created successfully" in result_text:
        return "PASS"
    return "FAIL"


# ---------------------------------------------------------------------------
# STEP 4: Run everything and show the problem
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    setup_contacts_folder()
    print("=== BEFORE MCP: No common rules ===\n")

    # Run Agent 1
    print("Agent 1 result:")
    result_1 = agent_1_custom_approach()
    print(f"  Output: {result_1}")
    print(f"  Evaluator says: {evaluator_for_agent_1(result_1)}")
    print("  But did Agent 1 create emails.csv? NO.")
    print("  We only checked text. This is 'fake checking'.\n")

    # Run Agent 2
    print("Agent 2 result:")
    result_2 = agent_2_custom_approach()
    print(f"  Output: {result_2}")
    print(f"  Evaluator says: {evaluator_for_agent_2(result_2)}")
    print("  But let's check the CSV file...")
    with open("emails.csv") as f:
        print(f"  File content:\n{f.read()}")
    print("  Oops! Bob's email is missing. But the evaluator still said PASS.")
    print("  Because the evaluator only checked the text, not the real file.\n")

    # Summary
    print("=== THE PROBLEM ===")
    print("1. Every agent uses a different custom approach.")
    print("2. Every evaluator checks different things.")
    print("3. Nobody checks the REAL result (the actual file on disk).")
    print("4. You cannot fairly compare Agent 1 and Agent 2.")
    print("\nThis is why MCP was invented: to make ONE common rulebook.")
