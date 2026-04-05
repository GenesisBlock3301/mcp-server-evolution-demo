#!/usr/bin/env python3
"""
Seed script to populate the database with ~100 sample tasks.
Run: python seed_tasks.py
"""

import sqlite3
import random
from datetime import datetime, timedelta
from database import DB_PATH, init_db

# Sample task templates
TASK_TITLES = [
    "Review project documentation", "Fix login bug", "Update README",
    "Refactor authentication module", "Write unit tests", "Deploy to staging",
    "Meeting with team", "Code review", "Optimize database queries",
    "Update dependencies", "Fix CSS styling", "Implement caching",
    "Write API documentation", "Test mobile responsiveness", "Backup database",
    "Configure CI/CD pipeline", "Setup monitoring alerts", "Review pull requests",
    "Update user manual", "Fix broken links", "Implement search feature",
    "Add pagination", "Optimize images", "Setup SSL certificate",
    "Configure logging", "Create onboarding guide", "Fix memory leak",
    "Update error handling", "Implement rate limiting", "Audit security",
    "Clean up unused code", "Migrate to new framework", "Setup Docker",
    "Write integration tests", "Update environment variables", "Fix CORS issues",
    "Implement WebSocket support", "Add export functionality", "Setup Redis",
    "Configure email service", "Implement OAuth", "Add file upload",
    "Create dashboard widgets", "Fix date formatting", "Add data validation",
    "Implement bulk operations", "Add sorting/filtering", "Fix navigation menu",
    "Update footer links", "Add loading spinners", "Implement dark mode",
    "Add keyboard shortcuts", "Fix dropdown issues", "Update API version",
    "Implement notifications", "Add activity logs", "Setup error tracking",
    "Configure backup schedule", "Update legal pages", "Add print styles",
    "Implement drag-and-drop", "Add tooltips", "Fix modal dialogs",
    "Update color scheme", "Add confirmation dialogs", "Implement undo/redo",
    "Add keyboard accessibility", "Fix form validation", "Update sitemap",
    "Add social sharing", "Implement lazy loading", "Fix image gallery",
    "Add breadcrumbs", "Update navigation", "Fix mobile menu",
    "Implement infinite scroll", "Add data export", "Fix timezone issues",
    "Add currency formatting", "Implement localization", "Add user roles",
    "Setup email templates", "Add push notifications", "Fix video player",
    "Implement audio playback", "Add emoji support", "Fix text overflow",
    "Add character counter", "Implement autosave", "Fix session timeout",
    "Add password reset", "Implement 2FA", "Update privacy policy",
    "Add cookie consent", "Implement GDPR compliance", "Fix XSS vulnerability",
    "Update CSRF tokens", "Add content security policy", "Fix SQL injection",
    "Implement API throttling", "Add request logging", "Update rate limits"
]

PRIORITIES = ["low", "medium", "high"]
STATUSES = ["pending", "in_progress", "completed"]


def random_date(start_days=-30, end_days=30):
    """Generate a random date within range."""
    days = random.randint(start_days, end_days)
    date = datetime.now() + timedelta(days=days)
    return date.strftime("%Y-%m-%d")


def generate_description(title):
    """Generate a description based on title."""
    actions = [
        "Need to complete this ASAP",
        "Low priority, can wait",
        "Important for next release",
        "Customer requested feature",
        "Technical debt cleanup",
        "Part of sprint goals",
        "Blocking other tasks",
        "Research required first",
        "Coordinate with design team",
        "Review with stakeholders"
    ]
    return f"{random.choice(actions)}. {title.lower()} for better user experience."


def seed_tasks(count=100):
    """Insert sample tasks into database."""
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing tasks (optional - comment out to keep existing)
    cursor.execute("DELETE FROM tasks")
    print("🗑️  Cleared existing tasks")
    
    inserted = 0
    for i in range(count):
        title = TASK_TITLES[i % len(TASK_TITLES)]
        if i >= len(TASK_TITLES):
            title += f" (v{i // len(TASK_TITLES) + 2})"
        
        priority = random.choice(PRIORITIES)
        status = random.choice(STATUSES)
        due_date = random_date(-15, 45)
        description = generate_description(title)
        
        # Some completed tasks have completed_at
        completed_at = None
        if status == "completed":
            completed = datetime.now() - timedelta(days=random.randint(0, 30))
            completed_at = completed.strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO tasks (title, description, priority, status, due_date, completed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, priority, status, due_date, completed_at))
        inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Inserted {inserted} tasks into database")
    print("📊 Priority distribution: Low/Med/High (random)")
    print("📊 Status distribution: Pending/InProgress/Completed (random)")


if __name__ == "__main__":
    seed_tasks(100)
