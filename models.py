from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Task:
    """Task data structure"""
    title: str
    priority: str
    due_date: Optional[datetime]
    description: str
    completed: bool = False
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self):
        return {
            'title': self.title,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Meeting:
    """Meeting data structure"""
    title: str
    date: datetime
    attendees: List[str]
    agenda: str
    duration: int = 60  # minutes
    location: str = ""
    status: str = "scheduled"
    google_event_id: Optional[str] = None

    def to_dict(self):
        return {
            'title': self.title,
            'date': self.date.isoformat() if self.date else None,
            'time': self.date.strftime('%H:%M') if self.date else None,
            'attendees': self.attendees,
            'agenda': self.agenda,
            'duration': self.duration,
            'location': self.location,
            'status': self.status,
            'google_event_id': self.google_event_id
        }

@dataclass
class Email:
    """Email data structure"""
    sender: str
    subject: str
    content: str
    timestamp: datetime
    priority: str = "Normal"
    read: bool = False
    replied: bool = False
    gmail_id: Optional[str] = None
    thread_id: Optional[str] = None

    def to_dict(self):
        return {
            'sender': self.sender,
            'subject': self.subject,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'time': self.timestamp.strftime('%H:%M') if self.timestamp else None,
            'priority': self.priority,
            'read': self.read,
            'replied': self.replied,
            'gmail_id': self.gmail_id,
            'thread_id': self.thread_id
        }
