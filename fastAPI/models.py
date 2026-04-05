# models.py
# Pydantic models for data validation

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ============ Task Models ============

class TaskCreate(BaseModel):
    """Model for creating a new task."""
    title: str = Field(..., description="Title of the task", min_length=1)
    description: Optional[str] = Field(None, description="Detailed description")
    priority: Priority = Field(default=Priority.MEDIUM, description="Task priority: low, medium, high")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")


class TaskUpdate(BaseModel):
    """Model for updating an existing task."""
    title: Optional[str] = Field(None, description="New title")
    description: Optional[str] = Field(None, description="New description")
    priority: Optional[Priority] = Field(None, description="New priority")
    status: Optional[Status] = Field(None, description="New status")
    due_date: Optional[str] = Field(None, description="New due date")


class Task(BaseModel):
    """Full task model returned from database."""
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    due_date: Optional[str]
    created_at: str
    completed_at: Optional[str]
    
    class Config:
        from_attributes = True


# ============ Note Models ============

class NoteCreate(BaseModel):
    """Model for creating a new note."""
    title: str = Field(..., description="Title of the note", min_length=1)
    content: str = Field(..., description="Note content", min_length=1)
    tags: Optional[str] = Field(None, description="Comma-separated tags (e.g., 'python,learning,mcp')")


class NoteUpdate(BaseModel):
    """Model for updating an existing note."""
    title: Optional[str] = Field(None, description="New title")
    content: Optional[str] = Field(None, description="New content")
    tags: Optional[str] = Field(None, description="New tags")


class Note(BaseModel):
    """Full note model returned from database."""
    id: int
    title: str
    content: str
    tags: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


# ============ Response Models ============

class TaskListResponse(BaseModel):
    """Response model for listing tasks."""
    tasks: List[Task]
    count: int


class NoteListResponse(BaseModel):
    """Response model for listing notes."""
    notes: List[Note]
    count: int


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool
    message: str
    id: Optional[int] = None


class TodayOverview(BaseModel):
    """Overview of today's tasks and recent notes."""
    pending_tasks_count: int
    due_today_count: int
    high_priority_count: int
    recent_notes_count: int
    pending_tasks: List[Task]
    recent_notes: List[Note]
