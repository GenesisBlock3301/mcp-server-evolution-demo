# main.py
# FastAPI Application with MCP Server over HTTP (SSE)
# Multiple clients can connect to this single server

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import uvicorn

from database import init_db
from models import (
    TaskCreate, TaskUpdate, Task, TaskListResponse,
    NoteCreate, NoteUpdate, Note, NoteListResponse,
    SuccessResponse
)
from mcp_server import mcp, get_db


# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    print("🚀 Starting up...")
    init_db()
    print("✅ Database ready")
    yield
    print("🛑 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Task & Note Manager API",
    description="A FastAPI application with MCP server for task and note management",
    version="1.0.0",
    lifespan=lifespan
)

# Trust proxy headers (required when behind Nginx)
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Health & Info Endpoints ============

@app.get("/", response_class=PlainTextResponse)
async def root():
    """Root endpoint with basic info."""
    return """Task & Note Manager API
==================

Available endpoints:
- GET  /health          - Health check
- GET  /mcp/sse         - MCP Server (SSE transport)
- POST /mcp/messages    - MCP message endpoint (POST)

All MCP tools are available via the SSE endpoint.

Run with: uvicorn main:app --host 0.0.0.0 --port 8000
"""


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "TaskNoteManager", "version": "1.0.0"}


# ============ MCP Server Endpoint ============

# Mount the MCP server with SSE transport at /mcp/sse
# This allows multiple clients to connect simultaneously
# FastMCP creates an ASGI app with SSE support via http_app()
mcp_app = mcp.http_app(transport="sse")
app.mount("/mcp", mcp_app)


# ============ REST API Endpoints (Optional) ============
# These are regular REST endpoints - you can use them alongside MCP

@app.post("/api/tasks", response_model=SuccessResponse)
async def api_create_task(task: TaskCreate):
    """Create a new task via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (title, description, priority, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (task.title, task.description, task.priority, task.due_date, "pending"))
            conn.commit()
            return SuccessResponse(
                success=True,
                message="Task created",
                id=cursor.lastrowid
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks", response_model=TaskListResponse)
async def api_list_tasks(status: str = None, priority: str = None):
    """List tasks via REST API."""
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
            
            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            tasks = [Task(**dict(row)) for row in rows]
            
        return TaskListResponse(tasks=tasks, count=len(tasks))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", response_model=Task)
async def api_get_task(task_id: int):
    """Get a single task by ID via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row:
                return Task(**dict(row))
            else:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notes", response_model=SuccessResponse)
async def api_create_note(note: NoteCreate):
    """Create a new note via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notes (title, content, tags)
                VALUES (?, ?, ?)
            """, (note.title, note.content, note.tags))
            conn.commit()
            return SuccessResponse(
                success=True,
                message="Note created",
                id=cursor.lastrowid
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notes", response_model=NoteListResponse)
async def api_list_notes():
    """List all notes via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            notes = [Note(**dict(row)) for row in rows]
            
        return NoteListResponse(notes=notes, count=len(notes))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notes/{note_id}", response_model=Note)
async def api_get_note(note_id: int):
    """Get a single note by ID via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            
            if row:
                return Note(**dict(row))
            else:
                raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/tasks/{task_id}", response_model=SuccessResponse)
async def api_update_task(task_id: int, task_update: TaskUpdate):
    """Update a task by ID via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if task exists
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Build update query dynamically
            updates = []
            params = []
            if task_update.title is not None:
                updates.append("title = ?")
                params.append(task_update.title)
            if task_update.description is not None:
                updates.append("description = ?")
                params.append(task_update.description)
            if task_update.priority is not None:
                updates.append("priority = ?")
                params.append(task_update.priority)
            if task_update.status is not None:
                updates.append("status = ?")
                params.append(task_update.status)
                # Update completed_at if status changed to completed
                if task_update.status == "completed":
                    updates.append("completed_at = CURRENT_TIMESTAMP")
            if task_update.due_date is not None:
                updates.append("due_date = ?")
                params.append(task_update.due_date)
            
            if not updates:
                return SuccessResponse(success=True, message="No changes to update", id=task_id)
            
            set_clause = ', '.join(updates)
            query = "UPDATE tasks SET " + set_clause + " WHERE id = ?"
            params.append(task_id)
            cursor.execute(query, params)
            conn.commit()
            
            return SuccessResponse(success=True, message="Task updated", id=task_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tasks/{task_id}", response_model=SuccessResponse)
async def api_delete_task(task_id: int):
    """Delete a task by ID via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            return SuccessResponse(success=True, message="Task deleted", id=task_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/notes/{note_id}", response_model=SuccessResponse)
async def api_update_note(note_id: int, note_update: NoteUpdate):
    """Update a note by ID via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if note exists
            cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
            
            # Build update query dynamically
            updates = []
            params = []
            if note_update.title is not None:
                updates.append("title = ?")
                params.append(note_update.title)
            if note_update.content is not None:
                updates.append("content = ?")
                params.append(note_update.content)
            if note_update.tags is not None:
                updates.append("tags = ?")
                params.append(note_update.tags)
            
            # Always update updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")
            
            if len(updates) == 1:  # Only updated_at, no actual changes
                return SuccessResponse(success=True, message="No changes to update", id=note_id)
            
            set_clause = ', '.join(updates)
            query = "UPDATE notes SET " + set_clause + " WHERE id = ?"
            params.append(note_id)
            cursor.execute(query, params)
            conn.commit()
            
            return SuccessResponse(success=True, message="Note updated", id=note_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/notes/{note_id}", response_model=SuccessResponse)
async def api_delete_note(note_id: int):
    """Delete a note by ID via REST API."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
            
            return SuccessResponse(success=True, message="Note deleted", id=note_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Main Entry Point ============

if __name__ == "__main__":
    print("=" * 50)
    print("Task & Note Manager - FastAPI + MCP Server")
    print("=" * 50)
    print("\nStarting server with HTTP (SSE) transport...")
    print("MCP endpoint: http://localhost:8000/mcp/sse")
    print("Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
