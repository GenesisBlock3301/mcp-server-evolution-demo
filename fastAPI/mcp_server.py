# mcp_server.py
# MCP Server with tools for Task & Note Management
# Uses HTTP SSE transport - can be accessed by multiple clients

import json
from datetime import datetime
from fastmcp import FastMCP
from database import get_db, init_db

# Create MCP server instance
mcp = FastMCP("TaskNoteManager")


# ============ Task Tools ============

@mcp.tool()
def create_task(title: str, description: str = "", priority: str = "medium", due_date: str = "") -> str:
    """
    Create a new task.
    
    Args:
        title: Task title (required)
        description: Task details
        priority: low, medium, or high (default: medium)
        due_date: Due date in YYYY-MM-DD format (optional)
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (title, description, priority, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (title, description, priority, due_date if due_date else None, "pending"))
            conn.commit()
            task_id = cursor.lastrowid
        return json.dumps({
            "success": True,
            "message": f"Task '{title}' created successfully",
            "id": task_id
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def list_tasks(status: str = "", priority: str = "") -> str:
    """
    List tasks with optional filters.
    
    Args:
        status: Filter by status (pending, in_progress, completed) - empty for all
        priority: Filter by priority (low, medium, high) - empty for all
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            
            query += """ ORDER BY 
                CASE priority 
                    WHEN 'high' THEN 1 
                    WHEN 'medium' THEN 2 
                    ELSE 3 
                END,
                CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
                due_date ASC"""
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            tasks = [dict(row) for row in rows]
            
        return json.dumps({
            "success": True,
            "count": len(tasks),
            "tasks": tasks
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def get_task(task_id: int) -> str:
    """
    Get a single task by ID.
    
    Args:
        task_id: The task ID number
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row:
                return json.dumps({
                    "success": True,
                    "task": dict(row)
                }, indent=2)
            else:
                return json.dumps({"success": False, "error": f"Task {task_id} not found"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def update_task(task_id: int, title: str = "", description: str = "", 
                priority: str = "", status: str = "", due_date: str = "") -> str:
    """
    Update an existing task. Only provide fields you want to change. don't do any delete, remove action here.
    
    Args:
        task_id: The task ID to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        status: New status (optional)
        due_date: New due date (optional)
    """
    try:
        updates = []
        params = []
        
        if title:
            updates.append("title = ?")
            params.append(title)
        if description:
            updates.append("description = ?")
            params.append(description)
        if priority:
            updates.append("priority = ?")
            params.append(priority)
        if status:
            updates.append("status = ?")
            params.append(status)
            if status == "completed":
                updates.append("completed_at = CURRENT_TIMESTAMP")
        if due_date:
            updates.append("due_date = ?")
            params.append(due_date)
        
        if not updates:
            return json.dumps({"success": False, "error": "No fields to update"})
        
        params.append(task_id)
        set_clause = ', '.join(updates)
        query = "UPDATE tasks SET " + set_clause + " WHERE id = ?"
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            if cursor.rowcount > 0:
                return json.dumps({
                    "success": True,
                    "message": f"Task {task_id} updated successfully"
                })
            else:
                return json.dumps({"success": False, "error": f"Task {task_id} not found"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def complete_task(task_id: int) -> str:
    """
    Mark a task as completed.
    
    Args:
        task_id: The task ID to complete
    """
    return update_task(task_id, status="completed")


@mcp.tool()
def delete_task(task_id: int) -> str:
    """
    Delete a task permanently.
    
    Args:
        task_id: The task ID to delete
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return json.dumps({
                    "success": True,
                    "message": f"Task {task_id} deleted successfully"
                })
            else:
                return json.dumps({"success": False, "error": f"Task {task_id} not found"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def search_tasks(query: str) -> str:
    """
    Search tasks by title or description.
    
    Args:
        query: Search keyword
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
            """, (search_term, search_term))
            rows = cursor.fetchall()
            tasks = [dict(row) for row in rows]
            
        return json.dumps({
            "success": True,
            "count": len(tasks),
            "tasks": tasks
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# ============ Note Tools ============

@mcp.tool()
def create_note(title: str, content: str, tags: str = "") -> str:
    """
    Create a new note.
    
    Args:
        title: Note title (required)
        content: Note content (required)
        tags: Comma-separated tags (e.g., "python,learning,mcp")
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notes (title, content, tags)
                VALUES (?, ?, ?)
            """, (title, content, tags if tags else None))
            conn.commit()
            note_id = cursor.lastrowid
        return json.dumps({
            "success": True,
            "message": f"Note '{title}' created successfully",
            "id": note_id
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def list_notes() -> str:
    """
    List all notes ordered by most recent.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            notes = [dict(row) for row in rows]
            
        return json.dumps({
            "success": True,
            "count": len(notes),
            "notes": notes
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def get_note(note_id: int) -> str:
    """
    Get a single note by ID.
    
    Args:
        note_id: The note ID number
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            
            if row:
                return json.dumps({
                    "success": True,
                    "note": dict(row)
                }, indent=2)
            else:
                return json.dumps({"success": False, "error": f"Note {note_id} not found"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def update_note(note_id: int, title: str = "", content: str = "", tags: str = "") -> str:
    """
    Update an existing note. Only provide fields you want to change.
    
    Args:
        note_id: The note ID to update
        title: New title (optional)
        content: New content (optional)
        tags: New tags (optional)
    """
    try:
        updates = []
        params = []
        
        if title:
            updates.append("title = ?")
            params.append(title)
        if content:
            updates.append("content = ?")
            params.append(content)
        if tags:
            updates.append("tags = ?")
            params.append(tags)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        if len(updates) == 1:  # Only timestamp
            return json.dumps({"success": False, "error": "No fields to update"})
        
        params.append(note_id)
        set_clause = ', '.join(updates)
        query = "UPDATE notes SET " + set_clause + " WHERE id = ?"
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            if cursor.rowcount > 0:
                return json.dumps({
                    "success": True,
                    "message": f"Note {note_id} updated successfully"
                })
            else:
                return json.dumps({"success": False, "error": f"Note {note_id} not found"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def delete_note(note_id: int) -> str:
    """
    Delete a note permanently.
    
    Args:
        note_id: The note ID to delete
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return json.dumps({
                    "success": True,
                    "message": f"Note {note_id} deleted successfully"
                })
            else:
                return json.dumps({"success": False, "error": f"Note {note_id} not found"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def search_notes(query: str) -> str:
    """
    Search notes by title, content, or tags.
    
    Args:
        query: Search keyword
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT * FROM notes 
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY updated_at DESC
            """, (search_term, search_term, search_term))
            rows = cursor.fetchall()
            notes = [dict(row) for row in rows]
            
        return json.dumps({
            "success": True,
            "count": len(notes),
            "notes": notes
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def search_by_tag(tag: str) -> str:
    """
    Find notes by a specific tag.
    
    Args:
        tag: Tag to search for
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            # Search for tag surrounded by commas or at start/end
            search_pattern = f"%{tag}%"
            cursor.execute("""
                SELECT * FROM notes 
                WHERE tags LIKE ?
                ORDER BY updated_at DESC
            """, (search_pattern,))
            rows = cursor.fetchall()
            notes = [dict(row) for row in rows]
            
        return json.dumps({
            "success": True,
            "count": len(notes),
            "notes": notes
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# ============ Overview Tools ============

@mcp.tool()
def get_today_overview() -> str:
    """
    Get an overview of today's tasks and recent notes.
    Shows pending tasks count, due today count, and recent activity.
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Pending tasks count
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status != 'completed'")
            pending_count = cursor.fetchone()[0]
            
            # Due today count
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE due_date = ? AND status != 'completed'", (today,))
            due_today_count = cursor.fetchone()[0]
            
            # High priority count
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = 'high' AND status != 'completed'")
            high_priority_count = cursor.fetchone()[0]
            
            # Recent notes (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) FROM notes 
                WHERE created_at >= date('now', '-7 days')
            """)
            recent_notes_count = cursor.fetchone()[0]
            
            # Get pending tasks list
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE status != 'completed'
                ORDER BY 
                    CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
                    due_date ASC
                LIMIT 5
            """)
            pending_tasks = [dict(row) for row in cursor.fetchall()]
            
            # Get recent notes
            cursor.execute("""
                SELECT * FROM notes 
                ORDER BY updated_at DESC
                LIMIT 3
            """)
            recent_notes = [dict(row) for row in cursor.fetchall()]
            
        return json.dumps({
            "success": True,
            "today": today,
            "summary": {
                "pending_tasks": pending_count,
                "due_today": due_today_count,
                "high_priority": high_priority_count,
                "recent_notes": recent_notes_count
            },
            "top_pending_tasks": pending_tasks,
            "recent_notes": recent_notes
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Initialize database on module load
init_db()


if __name__ == "__main__":
    # Run with stdio transport when called directly
    print("Starting MCP server with stdio transport...")
    mcp.run(transport='stdio')
