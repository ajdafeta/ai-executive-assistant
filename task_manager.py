# task_manager.py - Enhanced Task Management System
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import anthropic
from models import Task
from config import Config

logger = logging.getLogger(__name__)

class TaskManager:
    """Enhanced task management with AI-powered features"""
    
    def __init__(self, anthropic_client=None):
        self.client = anthropic_client
        self.tasks_file = Path('data/tasks.json')
        self.tasks_file.parent.mkdir(exist_ok=True)
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> List[Task]:
        """Load tasks from storage"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    tasks_data = json.load(f)
                    return [self._dict_to_task(task_dict) for task_dict in tasks_data]
            return []
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            return []
    
    def _save_tasks(self):
        """Save tasks to storage"""
        try:
            tasks_data = [task.to_dict() for task in self.tasks]
            with open(self.tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
    
    def _dict_to_task(self, task_dict: Dict) -> Task:
        """Convert dictionary to Task object"""
        return Task(
            title=task_dict['title'],
            priority=task_dict['priority'],
            due_date=datetime.fromisoformat(task_dict['due_date']) if task_dict.get('due_date') else None,
            description=task_dict['description'],
            completed=task_dict.get('completed', False),
            created_at=datetime.fromisoformat(task_dict['created_at']) if task_dict.get('created_at') else datetime.now()
        )
    
    def create_task_from_message(self, message: str) -> Dict[str, Any]:
        """Create a task using AI to parse the message"""
        if not self.client:
            return {"success": False, "error": "AI client not available"}
        
        try:
            prompt = f"""Extract task details from this message:
"{message}"

Return a JSON object with:
- title: brief task title
- description: detailed description
- priority: "high", "medium", or "low"
- due_date: ISO format date if mentioned, null otherwise

Example: {{"title": "Review proposal", "description": "Review the Q4 budget proposal from finance team", "priority": "medium", "due_date": "2025-06-30T17:00:00"}}

Return only the JSON object."""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            task_data = json.loads(response_text.strip())
            
            # Create the task
            due_date = None
            if task_data.get('due_date'):
                due_date = datetime.fromisoformat(task_data['due_date'])
            
            task = Task(
                title=task_data['title'],
                priority=task_data.get('priority', 'medium'),
                due_date=due_date,
                description=task_data.get('description', task_data['title'])
            )
            
            self.tasks.append(task)
            self._save_tasks()
            
            return {
                "success": True,
                "task": task.to_dict(),
                "message": f"Created task: {task.title}"
            }
            
        except Exception as e:
            logger.error(f"Error creating task from message: {e}")
            return {"success": False, "error": str(e)}
    
    def get_tasks(self, include_completed: bool = False) -> List[Dict]:
        """Get all tasks"""
        tasks = self.tasks if include_completed else [t for t in self.tasks if not t.completed]
        return [task.to_dict() for task in sorted(tasks, key=lambda x: x.created_at, reverse=True)]
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get pending tasks sorted by priority and due date"""
        pending = [t for t in self.tasks if not t.completed]
        
        # Sort by priority (high first) then by due date
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        
        def sort_key(task):
            priority_value = priority_order.get(task.priority, 1)
            due_value = task.due_date if task.due_date else datetime.max.replace(tzinfo=None)
            return (priority_value, due_value)
        
        sorted_tasks = sorted(pending, key=sort_key)
        return [task.to_dict() for task in sorted_tasks]
    
    def get_overdue_tasks(self) -> List[Dict]:
        """Get overdue tasks"""
        now = datetime.now()
        overdue = [t for t in self.tasks if not t.completed and t.due_date and t.due_date < now]
        return [task.to_dict() for task in overdue]
    
    def complete_task(self, task_title: str) -> Dict[str, Any]:
        """Mark a task as completed"""
        for task in self.tasks:
            if task.title.lower() == task_title.lower() and not task.completed:
                task.completed = True
                self._save_tasks()
                return {"success": True, "message": f"Completed task: {task.title}"}
        
        return {"success": False, "error": "Task not found"}
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get a summary of all tasks"""
        pending = [t for t in self.tasks if not t.completed]
        overdue = self.get_overdue_tasks()
        
        return {
            "total": len(self.tasks),
            "pending": len(pending),
            "completed": len([t for t in self.tasks if t.completed]),
            "overdue": len(overdue),
            "high_priority": len([t for t in pending if t.priority == 'high']),
            "due_today": len([t for t in pending if t.due_date and t.due_date.date() == datetime.now().date()])
        }

class SmartSchedulingAgent:
    """AI-powered scheduling agent for calendar management"""
    
    def __init__(self, anthropic_client, calendar_service):
        self.client = anthropic_client
        self.calendar = calendar_service
    
    def suggest_meeting_times(self, request: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """Suggest optimal meeting times based on calendar and preferences"""
        try:
            # Get free time slots
            free_slots = self.calendar.find_free_time(duration_minutes=duration_minutes, days_ahead=14)
            
            if not free_slots:
                return {
                    "success": False,
                    "message": "No free time slots found in the next 14 days"
                }
            
            # Use AI to rank suggestions based on context
            slots_text = "\n".join([
                f"- {slot['start'].strftime('%A, %B %d at %I:%M %p')} for {slot['duration']} minutes"
                for slot in free_slots[:8]
            ])
            
            prompt = f"""Based on this meeting request: "{request}"
            
Available time slots:
{slots_text}

Rank the top 3 most suitable times considering:
- Professional hours (9 AM - 5 PM preferred)
- Avoiding Monday mornings and Friday afternoons
- Meeting type appropriateness

Return format:
1. [Date and time] - [Reason]
2. [Date and time] - [Reason]  
3. [Date and time] - [Reason]"""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggestions = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            
            return {
                "success": True,
                "suggestions": suggestions,
                "free_slots": free_slots[:5]  # Return top 5 technical slots
            }
            
        except Exception as e:
            logger.error(f"Error suggesting meeting times: {e}")
            return {"success": False, "error": str(e)}
    
    def parse_meeting_request(self, message: str) -> Dict[str, Any]:
        """Parse a natural language meeting request"""
        try:
            prompt = f"""Parse this meeting request and extract details:
"{message}"

Return JSON with:
- title: meeting title
- attendees: list of email addresses if mentioned
- duration: estimated duration in minutes
- description: agenda or purpose
- urgency: "high", "medium", "low"
- preferred_times: any time preferences mentioned

Example: {{"title": "Budget Review", "attendees": ["john@company.com"], "duration": 60, "description": "Review Q4 budget proposals", "urgency": "medium", "preferred_times": "next week afternoons"}}"""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            meeting_data = json.loads(response_text.strip())
            
            return {"success": True, "meeting_data": meeting_data}
            
        except Exception as e:
            logger.error(f"Error parsing meeting request: {e}")
            return {"success": False, "error": str(e)}

class EmailInsightAgent:
    """AI agent for email analysis and insights"""
    
    def __init__(self, anthropic_client, gmail_service):
        self.client = anthropic_client
        self.gmail = gmail_service
    
    def analyze_emails(self, emails: List) -> Dict[str, Any]:
        """Analyze recent emails for insights"""
        if not self.client or not emails:
            return {"success": False, "insights": []}
        
        try:
            # Prepare email summary for analysis
            email_summaries = []
            for email in emails[:10]:  # Analyze last 10 emails
                summary = f"From: {email.sender}\nSubject: {email.subject}\nPriority: {email.priority}"
                email_summaries.append(summary)
            
            emails_text = "\n---\n".join(email_summaries)
            
            prompt = f"""Analyze these recent emails and provide actionable insights:

{emails_text}

Provide insights about:
1. Urgent items requiring immediate attention
2. Recurring themes or topics
3. People who need responses
4. Time-sensitive opportunities

Format as bullet points, be concise and actionable."""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            insights = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            
            return {
                "success": True,
                "insights": insights,
                "emails_analyzed": len(emails)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emails: {e}")
            return {"success": False, "error": str(e)}
    
    def suggest_email_responses(self, email_content: str, context: str = "") -> Dict[str, Any]:
        """Suggest email response templates"""
        try:
            prompt = f"""Generate 3 professional email response options for:

Email content: "{email_content}"
Context: {context}

Provide:
1. Quick acknowledgment (1-2 sentences)
2. Detailed response (1 paragraph)
3. Meeting request (if applicable)

Keep responses professional and concise."""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggestions = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            
            return {"success": True, "suggestions": suggestions}
            
        except Exception as e:
            logger.error(f"Error suggesting email responses: {e}")
            return {"success": False, "error": str(e)}