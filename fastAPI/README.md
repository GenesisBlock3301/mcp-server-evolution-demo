# FastAPI + MCP Server (HTTP/SSE Transport) - Production Guide

A complete **Task & Note Manager** application built with **FastAPI** and **MCP (Model Context Protocol)** using **HTTP SSE transport**.

> **Why HTTP/SSE?** This server can be accessed by **multiple clients simultaneously** - Kimi CLI, other AI assistants, web apps, mobile apps - all sharing the same database and tools!

---

## 📁 Project Structure

```
fastAPI/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── main.py            # FastAPI app with MCP server (HTTP/SSE)
├── mcp_server.py      # MCP server with all tools
├── database.py        # SQLite database setup
├── models.py          # Pydantic data models
└── seed_tasks.py      # Database seeding script
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd fastAPI
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Verify It's Running

```bash
# Health check
curl http://localhost:8000/health

# Expected output:
# {"status": "healthy", "service": "TaskNoteManager", "version": "1.0.0"}

# Test MCP SSE endpoint
curl -N http://localhost:8000/mcp/sse
# Should show: event: endpoint
```

### 4. Seed Sample Data (Optional)

```bash
python seed_tasks.py
# Inserts 100 sample tasks for testing
```

---

## 🔌 Connect Kimi CLI to Your Server

### Step 1: Edit Kimi CLI Config

Open `~/.kimi/mcp.json` and add your server:

```json
{
  "mcpServers": {
    "taskmanager": {
      "url": "http://localhost:8000/mcp/sse"
    }
  }
}
```

### Step 2: Restart Kimi CLI

Your server will be automatically discovered with all tools!

### Step 3: Verify Connection

```bash
kimi-cli mcp list
# Should show: taskmanager (connected) with 16+ tools
```

---

## 🛠️ Available MCP Tools

### Task Management

| Tool | Description | Example Use |
|------|-------------|-------------|
| `create_task` | Create a new task | Create a task with title, priority, due date |
| `list_tasks` | List all tasks (with filters) | Show pending high-priority tasks |
| `get_task` | Get a single task by ID | Get task details for ID 5 |
| `update_task` | Update task fields | Change priority or due date |
| `complete_task` | Mark task as done | Complete task ID 3 |
| `delete_task` | Delete a task permanently | Remove task ID 7 |
| `search_tasks` | Search by title/description | Find tasks with "meeting" |

### Note Management

| Tool | Description | Example Use |
|------|-------------|-------------|
| `create_note` | Create a new note | Save a note with title and content |
| `list_notes` | List all notes | Show all my notes |
| `get_note` | Get a note by ID | Retrieve note ID 2 |
| `update_note` | Update note content | Edit note with new text |
| `delete_note` | Delete a note | Remove note ID 4 |
| `search_notes` | Search notes | Find notes about "python" |
| `search_by_tag` | Find notes by tag | Get all notes tagged "work" |

### Overview

| Tool | Description |
|------|-------------|
| `get_today_overview` | Summary of today's tasks and recent activity |

---

## 💬 Example Conversations with Kimi

### Creating Tasks

**You:** "I need to finish the MCP project report by Friday"

**Kimi:** *Calls `create_task` with title="Finish MCP project report", due_date="2026-04-10"*

> ✅ I've created a high-priority task "Finish MCP project report" due Friday.

---

### Managing Tasks

**You:** "What tasks do I have?"

**Kimi:** *Calls `list_tasks` and shows your tasks*

> Here are your pending tasks:
> 1. **Finish MCP project report** (High priority, due Friday)
> 2. **Buy groceries** (Medium priority, no due date)
> 3. **Call dentist** (Low priority, due tomorrow)

---

**You:** "Mark the MCP report as complete"

**Kimi:** *Calls `search_tasks` to find the task, then `complete_task`*

> ✅ Task "Finish MCP project report" marked as completed!

---

### Working with Notes

**You:** "Save this idea: A FastAPI app that combines multiple MCP servers"

**Kimi:** *Calls `create_note` with your content*

> ✅ Note saved with title "FastAPI MCP Idea" and tagged as "ideas".

---

**You:** "Find my notes about python"

**Kimi:** *Calls `search_notes` with query="python"*

> Found 3 notes matching "python":
> 1. **Python Best Practices** (updated 2 days ago)
> 2. **Learning FastAPI** (updated 1 week ago)
> 3. **MCP Server Tutorial** (updated today)

---

### Daily Overview

**You:** "What should I focus on today?"

**Kimi:** *Calls `get_today_overview`*

> **Today's Overview:**
> - 📋 5 pending tasks
> - ⏰ 2 tasks due today
> - 🔥 1 high priority task
> - 📝 3 notes created this week
> 
> **Top Priority:** Review quarterly report (due today, high priority)

---

## 🌐 HTTP vs stdio: Why This Matters

### stdio Transport (Single User)

```
Kimi CLI ──starts──▶ [mcp_server.py]
        ◄──pipe──
        
❌ Server only lives while Kimi is running
❌ Other apps cannot connect
❌ Kimi must restart the server each time
```

### HTTP/SSE Transport (Multi-User) ✅ **This Project**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Kimi CLI   │     │  Web App    │     │  Mobile App │
│  (User 1)   │     │  (User 2)   │     │  (User 3)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ HTTP/SSE
                           ▼
              ┌─────────────────────┐
              │   FastAPI Server    │
              │   (Always Running)  │
              │   Port: 8000        │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   SQLite Database   │
              │   (tasks_notes.db)  │
              └─────────────────────┘

✅ Server runs independently
✅ Multiple clients connect simultaneously
✅ Data persists between sessions
✅ Can deploy to cloud/remote server
```

---

## 📊 REST API Endpoints

Your FastAPI app also provides regular REST endpoints alongside MCP:

### Task Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/tasks` | Create task | `TaskCreate` |
| GET | `/api/tasks` | List tasks | - |
| GET | `/api/tasks/{id}` | Get single task | - |
| PUT | `/api/tasks/{id}` | Update task | `TaskUpdate` |
| DELETE | `/api/tasks/{id}` | Delete task | - |

### Note Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/notes` | Create note | `NoteCreate` |
| GET | `/api/notes` | List notes | - |
| GET | `/api/notes/{id}` | Get single note | - |
| PUT | `/api/notes/{id}` | Update note | `NoteUpdate` |
| DELETE | `/api/notes/{id}` | Delete note | - |

### Request Body Examples

**TaskCreate (POST /api/tasks):**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "due_date": "2025-04-10"
}
```

**TaskUpdate (PUT /api/tasks/{id}):**
```json
{
  "title": "New title",
  "priority": "medium",
  "status": "completed"
}
```
**Note:** All fields are optional for updates.

**NoteCreate (POST /api/notes):**
```json
{
  "title": "My Note",
  "content": "Note content here...",
  "tags": "python,learning"
}
```

### Example REST Usage

```bash
# Create a task via REST
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "priority": "high"}'

# List all tasks
curl http://localhost:8000/api/tasks

# Update task 1
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Create a note
curl -X POST http://localhost:8000/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Ideas", "content": "Build an AI assistant", "tags": "ai,project"}'
```

---

## 🔒 Security & Production Deployment

### Security Checklist

| Layer | Risk | Mitigation |
|-------|------|------------|
| Transport | Plain HTTP | Use HTTPS/reverse proxy |
| Auth | No authentication | Add API keys/JWT |
| Input | SQL injection | Use parameterized queries ✅ |
| Audit | No activity logs | Implement audit logging |
| Access | Over-privileged tools | Split read/write permissions |

### 1. Reverse Proxy (Nginx/Caddy)

**What:** A web server that sits between clients and your MCP server, providing TLS termination, rate limiting, and security headers.

**Why You Need It:**
- **TLS/SSL encryption** (HTTPS)
- **Rate limiting** to prevent DDoS
- **Hide your server** - only nginx exposed to internet
- **Load balancing** across multiple instances

**Without It:**
```
Attacker sniffs traffic → Sees raw task data
DDoS on port 8000 → Server crashes
No SSL → MITM attacks steal API keys
```

**Nginx Configuration:**

```nginx
# /etc/nginx/sites-available/mcp
server {
    listen 443 ssl http2;
    server_name mcp.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/mcp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.yourdomain.com/privkey.pem;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=mcp:10m rate=10r/s;
    limit_req zone=mcp burst=20 nodelay;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Authorization $http_authorization;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name mcp.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**Enable the config:**
```bash
sudo ln -s /etc/nginx/sites-available/mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### 2. Unix Sockets (Local Only)

**What:** File-based communication instead of TCP ports. More secure and faster.

**Why You Need It:**
- **Faster:** No TCP handshake overhead
- **Secure:** File permissions control access (`chmod 660`)
- **Invisible:** Not in `netstat`, no port scanning

**Without It:**
```bash
$ nmap your-server
8000/tcp open  http     ← Attacker finds your MCP

# vs Unix socket: invisible, need filesystem access
```

**Implementation:**

```python
# main.py - Change to Unix socket
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        uds="/tmp/mcp_server.sock",  # Unix socket
        # NOT: host="0.0.0.0", port=8000
    )
```

**Nginx connects to socket:**
```nginx
location / {
    proxy_pass http://unix:/tmp/mcp_server.sock;
    # ... rest of config
}
```

**Set permissions:**
```bash
chmod 660 /tmp/mcp_server.sock
chown www-data:www-data /tmp/mcp_server.sock
```

---

### 3. Audit Logging

**What:** Track every MCP tool call for forensics and compliance.

**Why You Need It:**
- **Forensics:** Who deleted task 101?
- **Compliance:** GDPR/HIPAA requires audit trails
- **Debugging:** Trace "weird" behavior

**Without It:**
```
"All my tasks disappeared!" → No idea who/when
Insider threat → Can't prove unauthorized access
Bug reports → Can't reproduce without logs
```

**Implementation:**

```python
# mcp_server.py
import logging
from datetime import datetime

# Setup audit logger
audit_logger = logging.getLogger('mcp_audit')
audit_logger.setLevel(logging.INFO)
handler = logging.FileHandler('/var/log/mcp_audit.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(message)s'
))
audit_logger.addHandler(handler)

@mcp.tool()
def delete_task(task_id: int) -> str:
    """Delete a task permanently."""
    # Log BEFORE execution
    audit_logger.info(f"DELETE_TASK | id={task_id} | user={get_current_user()}")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            
            # Log SUCCESS
            audit_logger.info(f"DELETE_SUCCESS | id={task_id} | rows={cursor.rowcount}")
            return json.dumps({"success": True})
    except Exception as e:
        # Log FAILURE
        audit_logger.error(f"DELETE_ERROR | id={task_id} | error={str(e)}")
        return json.dumps({"success": False, "error": str(e)})
```

**Log Output:**
```
2025-04-04 12:45:22 | DELETE_TASK | id=101 | user=sifat
2025-04-04 12:45:22 | DELETE_SUCCESS | id=101 | rows=1
```

---

### 4. Principle of Least Privilege

**What:** Each tool has minimum required permissions. Split dangerous operations.

**Why You Need It:**
- **Blast radius:** Compromised read tool can't delete
- **Accidents:** User can't nuke data with typo
- **Compliance:** SOC2 requires access controls

**Without It:**
```
Single "admin" tool with full DB access
↓
Attacker exploits one endpoint
↓
DROP TABLE tasks;  ← Total data loss
```

**Implementation:**

```python
# ❌ BAD: One tool does everything
@mcp.tool()
def manage_task(action: str, task_id: int, ...):  # Too powerful

# ✅ GOOD: Separate read/write tools

@mcp.tool()
def get_task(task_id: int) -> str:
    """Read-only access"""
    # Only SELECT permission in DB

@mcp.tool()  
def create_task(title: str, ...) -> str:
    """Write access"""
    # INSERT permission only

@mcp.tool()
def delete_task(task_id: int, confirm: bool = False) -> str:
    """Destructive - requires confirmation"""
    if not confirm:
        return json.dumps({"error": "Must set confirm=true to delete"})
    # DELETE permission + extra check
```

**Database User Separation:**

```sql
-- Read-only user
CREATE USER 'mcp_reader'@'localhost' IDENTIFIED BY 'pass1';
GRANT SELECT ON tasks_notes.* TO 'mcp_reader';

-- Read-write user  
CREATE USER 'mcp_writer'@'localhost' IDENTIFIED BY 'pass2';
GRANT SELECT, INSERT, UPDATE ON tasks_notes.* TO 'mcp_writer';

-- Admin user (rarely used)
CREATE USER 'mcp_admin'@'localhost' IDENTIFIED BY 'pass3';
GRANT ALL ON tasks_notes.* TO 'mcp_admin';
```

---

## 🔧 Advanced Configuration

### Environment Variables

Create `.env` file:

```bash
# Server settings
PORT=8000
HOST=127.0.0.1
DEBUG=false

# Database
DB_PATH=/var/lib/mcp/tasks.db

# Security
API_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret
RATE_LIMIT=100/hour

# Logging
LOG_LEVEL=INFO
AUDIT_LOG=/var/log/mcp/audit.log
```

**Load in Python:**

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8000
    host: str = "127.0.0.1"
    db_path: str = "tasks_notes.db"
    api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Run on Different Port

```bash
# Option 1: Environment variable
export PORT=3000
python main.py

# Option 2: Uvicorn argument
uvicorn main:app --host 0.0.0.0 --port 3000
```

Update `~/.kimi/mcp.json`:

```json
{
  "mcpServers": {
    "taskmanager": {
      "url": "http://localhost:3000/mcp/sse"
    }
  }
}
```

---

## 📦 Production Deployment

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -m -u 1000 mcp && chown -R mcp:mcp /app
USER mcp

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DB_PATH=/app/data/tasks.db
      - LOG_LEVEL=INFO
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mcp-server
    restart: unless-stopped
```

**Deploy:**

```bash
docker-compose up -d
```

### Systemd Service

Create `/etc/systemd/system/mcp-server.service`:

```ini
[Unit]
Description=MCP Task Manager Server
After=network.target

[Service]
Type=simple
User=mcp
Group=mcp
WorkingDirectory=/opt/mcp-server
Environment=PYTHONPATH=/opt/mcp-server
Environment=DB_PATH=/var/lib/mcp/tasks.db
ExecStart=/opt/mcp-server/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Enable:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
sudo systemctl status mcp-server
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
uvicorn main:app --port 8001
```

### Kimi Can't Connect

1. **Check server is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify MCP endpoint:**
   ```bash
   curl -N http://localhost:8000/mcp/sse
   # Should show: event: endpoint
   ```

3. **Verify MCP config path:**
   ```bash
   cat ~/.kimi/mcp.json
   ```

4. **Check for typos in URL:**
   - ✅ `http://localhost:8000/mcp/sse`
   - ❌ `http://localhost:8000/sse`
   - ❌ `http://localhost:8000/mcp`

### Database Issues

```bash
# Delete and recreate database
rm fastAPI/tasks_notes.db
python main.py  # Will recreate automatically
```

### SSE Connection Drops

```bash
# Check nginx proxy_read_timeout
# Should be at least 86400 (24 hours) for SSE
```

---

## 🎯 Architecture Deep Dive

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Kimi CLI │  │ Claude   │  │  Web App │  │  Mobile  │        │
│  │          │  │ Desktop  │  │ (React)  │  │   App    │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │ HTTPS/WSS
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REVERSE PROXY (Nginx)                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  - TLS termination                                        │  │
│  │  - Rate limiting                                          │  │
│  │  - Static file serving                                    │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │         Localhost           │
              │    (Unix Socket / Port)     │
              ▼                             ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│   FASTAPI APPLICATION   │     │   REST API Endpoints    │
│                         │     │                         │
│  ┌───────────────────┐  │     │  POST /api/tasks        │
│  │  FastMCP Server   │  │     │  GET  /api/tasks/{id}   │
│  │                   │  │     │  PUT  /api/tasks/{id}   │
│  │  - create_task    │  │     │  etc.                   │
│  │  - list_tasks     │  │     └─────────────────────────┘
│  │  - delete_task    │  │
│  │  - etc. (16+)     │  │
│  └───────────────────┘  │
│                         │
│  Endpoint: /mcp/sse     │
└───────────┬─────────────┘
            │ SQLite
            ▼
┌─────────────────────────┐
│    tasks_notes.db       │
│  ┌─────────────────┐    │
│  │  tasks table    │    │
│  │  - id           │    │
│  │  - title        │    │
│  │  - priority     │    │
│  │  - status       │    │
│  │  - due_date     │    │
│  │  - created_at   │    │
│  └─────────────────┘    │
│  ┌─────────────────┐    │
│  │  notes table    │    │
│  │  - id           │    │
│  │  - title        │    │
│  │  - content      │    │
│  │  - tags         │    │
│  └─────────────────┘    │
└─────────────────────────┘
```

---

## 📚 Further Reading

- **MCP Documentation:** https://modelcontextprotocol.io/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **FastMCP Library:** https://github.com/jlowin/fastmcp
- **MCP Inspector (Debugging):** https://github.com/modelcontextprotocol/inspector

---

## ✅ Feature Summary

| Feature | Status |
|---------|--------|
| **Protocol** | MCP over HTTP/SSE |
| **Server** | FastAPI + FastMCP 3.x |
| **Database** | SQLite (swappable to PostgreSQL) |
| **Multi-client** | ✅ Yes - multiple apps can connect |
| **Persistence** | ✅ Data saved between sessions |
| **REST API** | ✅ Full CRUD endpoints included |
| **MCP Tools** | 16+ tools for tasks & notes |
| **Security** | Production-ready with reverse proxy |
| **Logging** | Audit trail support |
| **Docker** | Ready for containerization |

---

## 🚦 Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Transport | TCP port 8000 | Unix socket or TLS |
| Auth | None | API keys + JWT |
| Database | SQLite file | PostgreSQL |
| Logging | Console | Structured + Audit |
| Server | `python main.py` | Docker + Systemd |
| Reverse Proxy | None | Nginx with SSL |

---

**Enjoy building with MCP!** 🚀

For issues or contributions, see the main project repository.
