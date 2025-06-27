# run_assistant.py - Main Flask application for Executive Assistant
import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import threading
import webbrowser
from datetime import datetime, timedelta
import pytz

# Local imports
from google_backend import (
    GoogleAuthManager, GoogleCalendarService, GmailService, GoogleTasksService,
    CalendarAgent, ContextMemory
)
import anthropic
from config import Config
from models import Task, Meeting, Email

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import app from app.py to avoid circular imports
try:
    from app import app
except ImportError:
    # Fallback if app.py doesn't exist
    app = Flask(__name__)
    CORS(app)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

class ExecutiveAssistantApp:
    """Main application class for the Executive Assistant"""
    
    def __init__(self):
        # Validate configuration first
        try:
            Config.validate_config()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            # Continue without AI features if API key is missing
        
        self.auth_manager = GoogleAuthManager()
        self.calendar_service = None
        self.gmail_service = None
        self.tasks_service = None
        self.memory = ContextMemory()
        self.calendar_agent = None
        self.authenticated = False
        
        # Set up timezone
        try:
            self.local_timezone = pytz.timezone(Config.DEFAULT_TIMEZONE)
        except:
            self.local_timezone = pytz.UTC
            logger.warning("Using UTC timezone as fallback")

        # Initialize Anthropic client
        self._initialize_anthropic()
        
        # Try to load existing Google credentials on startup
        self._load_existing_credentials()

    def _initialize_anthropic(self):
        """Initialize Anthropic client with proper error handling"""
        api_key = Config.ANTHROPIC_API_KEY
        
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not found - AI features will be disabled")
            self.anthropic_client = None
            return
        
        try:
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            
            # Test the client with a simple request
            test_response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            logger.info("✅ Anthropic client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Anthropic client: {e}")
            self.anthropic_client = None
    
    def _load_existing_credentials(self):
        """Load existing Google credentials on startup if available"""
        try:
            import pickle
            import os
            
            token_path = 'credentials/token.pickle'
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    credentials = pickle.load(token)
                
                # Check if credentials are still valid
                if credentials and hasattr(credentials, 'valid'):
                    if credentials.valid or (hasattr(credentials, 'refresh_token') and credentials.refresh_token):
                        # Initialize Google services
                        from google_backend import GoogleCalendarService, GmailService, GoogleTasksService, CalendarAgent
                        
                        self.calendar_service = GoogleCalendarService(credentials)
                        self.gmail_service = GmailService(credentials)
                        self.tasks_service = GoogleTasksService(credentials)
                        
                        if self.anthropic_client:
                            self.calendar_agent = CalendarAgent(self.anthropic_client, self.calendar_service)
                        
                        self.authenticated = True
                        logger.info("✅ Restored Google authentication from saved credentials")
                        return True
                        
            logger.info("No valid saved credentials found - authentication required")
            return False
            
        except Exception as e:
            logger.warning(f"Could not load existing credentials: {e}")
            return False

    def authenticate_google(self):
        """Authenticate with Google services"""
        try:
            logger.info("Starting Google authentication...")
            creds = self.auth_manager.authenticate()
            
            self.calendar_service = GoogleCalendarService(creds)
            self.gmail_service = GmailService(creds)
            
            # Initialize Google Tasks service with error handling
            try:
                logger.info("🔄 Initializing Google Tasks service...")
                self.tasks_service = GoogleTasksService(creds)
                logger.info("✅ Google Tasks service initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Tasks service: {e}")
                self.tasks_service = None

            if self.anthropic_client:
                self.calendar_agent = CalendarAgent(self.anthropic_client, self.calendar_service)

            self.authenticated = True
            logger.info("✅ Google services authenticated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False

    def get_dashboard_data(self):
        """Get data for the dashboard"""
        logger.info(f"Dashboard request - authenticated: {self.authenticated}, calendar_service: {self.calendar_service is not None}, gmail_service: {self.gmail_service is not None}")
        
        if not self.authenticated:
            # Still provide task data and AI features even without Google
            tasks_count = 0
            try:
                from task_manager import TaskManager
                if not hasattr(self, 'task_manager'):
                    self.task_manager = TaskManager(self.anthropic_client)
                task_summary = self.task_manager.get_task_summary()
                tasks_count = task_summary['pending']
            except Exception as e:
                logger.warning(f"Could not load task data: {e}")
                
            return {
                'success': True,
                'authenticated': False,
                'meetings': [],
                'emails': [],
                'stats': {'meetings': 0, 'emails': 0, 'tasks': tasks_count, 'free_time': 0},
                'message': 'AI assistant ready. Connect Google for email and calendar features.'
            }

        try:
            logger.info("Fetching dashboard data...")
            
            # Get meetings for the next 7 days
            meetings = []
            if self.calendar_service:
                # Get events from now until next week
                from datetime import timedelta
                next_week = datetime.utcnow() + timedelta(days=7)
                meetings = self.calendar_service.get_upcoming_events(max_results=50)

            # Get emails
            emails = []
            if self.gmail_service:
                emails = self.gmail_service.get_messages(query='is:unread', max_results=20)

            # Get Google Tasks
            google_tasks = []
            if self.tasks_service:
                try:
                    logger.info("🔄 Attempting to fetch Google Tasks...")
                    google_tasks = self.tasks_service.get_todays_tasks()
                    logger.info(f"✅ Successfully fetched {len(google_tasks)} Google Tasks")
                except Exception as e:
                    logger.error(f"❌ Google Tasks API failed: {e}")
                    logger.error("This indicates the Tasks API scope was not granted during authentication")
                    google_tasks = []

            # Process meetings data and detect tasks
            meetings_data = []
            calendar_tasks = []  # Tasks derived from calendar events
            
            # Use a safe timezone fallback
            try:
                if hasattr(self, 'local_timezone') and self.local_timezone:
                    today_local = datetime.now(self.local_timezone).date()
                else:
                    today_local = datetime.now().date()
            except Exception:
                today_local = datetime.now().date()
            today_meetings = []

            for meeting in meetings:
                # Safe timezone conversion for meetings
                try:
                    if hasattr(self, 'local_timezone') and self.local_timezone and hasattr(meeting.date, 'astimezone'):
                        meeting_local = meeting.date.astimezone(self.local_timezone)
                    else:
                        meeting_local = meeting.date
                    meeting_local_date = meeting_local.date()
                except Exception:
                    meeting_local = meeting.date
                    meeting_local_date = meeting.date.date() if hasattr(meeting.date, 'date') else meeting.date

                # Detect if this is a task (single person, task keywords, etc.)
                is_task = self._is_calendar_event_a_task(meeting)
                
                if is_task:
                    # Add to calendar tasks
                    priority = "High" if meeting_local_date <= today_local else "Medium"
                    calendar_tasks.append({
                        'title': meeting.title,
                        'due_date': meeting_local.strftime('%Y-%m-%d %H:%M'),
                        'priority': priority,
                        'source': 'calendar',
                        'completed': False
                    })
                else:
                    # Add to meetings
                    meetings_data.append({
                        'title': meeting.title,
                        'time': meeting_local.strftime('%H:%M'),
                        'date': meeting_local.strftime('%Y-%m-%d'),
                        'attendees': meeting.attendees or [],
                        'duration': meeting.duration,
                        'location': meeting.location,
                        'event_id': meeting.google_event_id  # Add event ID for deletion
                    })

                # Check if this meeting is today
                if meeting_local_date == today_local:
                    today_meetings.append(meeting)

            # Process emails data
            emails_data = []
            unread_emails = []

            for email in emails[:10]:  # Limit to 10 for display
                # Safe timezone handling for emails
                try:
                    if hasattr(self, 'local_timezone') and self.local_timezone:
                        email_local = email.timestamp.astimezone(self.local_timezone)
                    else:
                        email_local = email.timestamp
                except Exception:
                    email_local = email.timestamp
                
                emails_data.append({
                    'sender': email.sender,
                    'subject': email.subject,
                    'time': email_local.strftime('%H:%M'),
                    'priority': email.priority,
                    'read': email.read,
                    'gmail_id': email.gmail_id  # Add Gmail ID for deletion
                })

                if not email.read:
                    unread_emails.append(email)

            # Get task information - only Google Tasks
            tasks_count = 0
            all_tasks = []
            try:
                # Add Google Tasks only
                for google_task in google_tasks:
                    google_task_dict = {
                        'title': google_task.title,
                        'due_date': google_task.due_date.strftime('%Y-%m-%d %H:%M') if google_task.due_date else 'No due date',
                        'priority': google_task.priority,
                        'source': 'google_tasks',
                        'completed': google_task.completed,
                        'task_id': getattr(google_task, 'google_task_id', None)  # Add Google Task ID for deletion
                    }
                    all_tasks.append(google_task_dict)
                
                # Count only Google Tasks
                tasks_count = len([t for t in google_tasks if not t.completed])
            except Exception as e:
                logger.warning(f"Could not load Google Tasks: {e}")

            # Calculate statistics with intelligent free time calculation
            total_meeting_time = sum(m.duration for m in today_meetings)
            
            # Smart free time calculation only when authenticated
            if self.authenticated:
                if len(today_meetings) == 0:
                    # No meetings - show available time based on current time of day
                    current_hour = datetime.now().hour
                    if current_hour < 9:
                        free_time_display = "Full day available"
                    elif current_hour < 17:
                        remaining_hours = max(0, 17 - current_hour)
                        free_time_display = f"{remaining_hours}h remaining today"
                    else:
                        free_time_display = "Day complete"
                else:
                    # Calculate remaining free time
                    free_time_hours = max(0, 8 - (total_meeting_time / 60))
                    if free_time_hours > 6:
                        free_time_display = f"{free_time_hours:.1f}h free"
                    elif free_time_hours > 3:
                        free_time_display = f"{free_time_hours:.1f}h available"
                    elif free_time_hours > 1:
                        free_time_display = f"{free_time_hours:.1f}h left"
                    else:
                        free_time_display = "Busy day"
            else:
                # When not authenticated, show 0 for consistency
                free_time_display = 0

            stats = {
                'meetings': len(today_meetings),
                'emails': len(unread_emails),
                'tasks': tasks_count,
                'free_time': free_time_display
            }

            logger.info(f"Dashboard data: {len(meetings_data)} meetings, {len(emails_data)} emails")

            return {
                'success': True,
                'authenticated': True,
                'meetings': meetings_data,
                'emails': emails_data,
                'tasks': all_tasks[:10],  # Return top 10 tasks for Priority Tasks display
                'stats': stats
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'authenticated': self.authenticated,
                'error': str(e),
                'meetings': [],
                'emails': [],
                'tasks': [],
                'stats': {'meetings': 0, 'emails': 0, 'tasks': 0, 'free_time': 0}
            }

    def _is_calendar_event_a_task(self, meeting):
        """
        Determine if a calendar event should be treated as a task.
        Returns True only for clear personal tasks, not regular meetings.
        """
        try:
            # Task keywords that strongly suggest personal tasks
            task_keywords = [
                'deadline', 'due', 'submit', 'reminder', 'task', 'todo', 'to do',
                'finish', 'complete', 'draft', 'personal appointment', 'prep', 'prepare',
                'bedtime', 'morning', 'workout', 'exercise', 'study', 'practice',
                'clean', 'organize', 'shopping', 'errands', 'pick up', 'drop off',
                'appointment', 'dentist', 'doctor', 'checkup', 'visit'
            ]
            
            # Meeting keywords that suggest it's NOT a task
            meeting_keywords = [
                'meeting', 'call', 'conference', 'discussion', 'standup',
                'sync', 'review meeting', 'team', 'group', 'session', 'interview',
                'presentation', 'demo', 'workshop', 'training', 'seminar'
            ]
            
            title_lower = meeting.title.lower() if meeting.title else ""
            
            # If it clearly contains meeting keywords, treat as meeting
            has_meeting_keywords = any(keyword in title_lower for keyword in meeting_keywords)
            if has_meeting_keywords:
                return False
            
            # Check if it's truly a single-person event (no attendees)
            attendee_count = len(meeting.attendees) if meeting.attendees else 0
            is_single_person = attendee_count == 0
            
            # Check for task keywords
            has_task_keywords = any(keyword in title_lower for keyword in task_keywords)
            
            # Consider it a task if:
            # 1. It's single-person AND has task keywords, OR
            # 2. It has very explicit task keywords (regardless of attendees), OR
            # 3. It's single-person and likely a personal activity (short title, no location suggesting meeting room)
            explicit_task_keywords = ['deadline', 'due', 'submit', 'reminder', 'task', 'todo', 'to do']
            has_explicit_task_keywords = any(keyword in title_lower for keyword in explicit_task_keywords)
            
            # Personal activity patterns for single-person events
            personal_activity_patterns = [
                'prep', 'bedtime', 'morning', 'workout', 'exercise', 'study', 'practice',
                'clean', 'organize', 'shopping', 'errands'
            ]
            has_personal_patterns = any(pattern in title_lower for pattern in personal_activity_patterns)
            
            return (is_single_person and has_task_keywords) or has_explicit_task_keywords or (is_single_person and has_personal_patterns)
            
        except Exception as e:
            logger.error(f"Error determining if event is task: {e}")
            return False

    def process_chat_message(self, message):
        """Process chat message using AI"""
        if not self.anthropic_client:
            return {
                'success': False,
                'response': "AI service is not available. Please check your Anthropic API key configuration."
            }

        try:
            # Add user message to memory
            self.memory.add_message("user", message)
            
            # Determine intent
            intent = self._determine_intent(message)
            logger.info(f"Detected intent: {intent}")

            # Route to appropriate handler
            if intent == 'calendar' and self.calendar_agent:
                result = self.calendar_agent.handle_request(message)
                response_text = result.get('response', 'I encountered an error processing your calendar request.')
                
            elif intent == 'email':
                response_text = self._handle_email_request(message)
                
            elif intent == 'task':
                response_text = self._handle_task_request(message)
                
            else:
                response_text = self._handle_general_request(message)

            # Add assistant response to memory
            self.memory.add_message("assistant", response_text)

            return {
                'success': True,
                'response': response_text
            }

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                'success': False,
                'response': f"I encountered an error processing your message: {str(e)}"
            }

    def _determine_intent(self, message):
        """Determine the intent of the user message"""
        try:
            if not self.anthropic_client:
                return 'general'
                
            intent_prompt = f"""Analyze this user message and determine the intent:

Message: "{message}"

Classify into one of these categories:
- calendar: scheduling, meetings, availability, appointments
- email: checking emails, sending, replying, inbox management
- task: creating tasks, managing todos, reminders
- general: general questions or conversation

Return just the category name."""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=50,
                messages=[{"role": "user", "content": intent_prompt}]
            )

            # Handle different response content types properly
            content = response.content[0]
            if hasattr(content, 'text'):
                return content.text.strip().lower()
            else:
                return str(content).strip().lower()
            
        except Exception as e:
            logger.error(f"Error determining intent: {e}")
            return 'general'

    def _handle_email_request(self, message):
        """Handle email-related requests"""
        if not self.gmail_service:
            return "Email service is not available. Please authenticate with Google first."

        try:
            if any(word in message.lower() for word in ['unread', 'check', 'inbox']):
                emails = self.gmail_service.get_messages(query='is:unread', max_results=5)
                
                if not emails:
                    return "You have no unread emails! 📧✨"

                response = f"📧 You have {len(emails)} unread emails:\n\n"
                for i, email in enumerate(emails, 1):
                    response += f"{i}. **{email.subject}**\n"
                    response += f"   From: {email.sender}\n"
                    response += f"   Priority: {email.priority}\n\n"

                return response
                
        except Exception as e:
            logger.error(f"Error handling email request: {e}")
            return f"Error checking emails: {str(e)}"

        return "I can help you check unread emails, send messages, or manage your inbox. What would you like me to do?"

    def _handle_task_request(self, message):
        """Handle task-related requests"""
        try:
            from task_manager import TaskManager
            
            if not hasattr(self, 'task_manager'):
                self.task_manager = TaskManager(self.anthropic_client)
            
            # Handle different task operations
            if any(word in message.lower() for word in ['create', 'add', 'new task']):
                # Parse task details from message using AI
                result = self.task_manager.create_task_from_message(message)
                
                # If Google Tasks is available, also create in Google Tasks
                if result['success'] and hasattr(self, 'tasks_service') and self.tasks_service:
                    try:
                        # Extract task details
                        task_title = result.get('task', {}).get('title', '')
                        task_description = result.get('task', {}).get('description', '')
                        task_due_date = result.get('task', {}).get('due_date', None)
                        
                        # Create in Google Tasks
                        google_result = self.tasks_service.create_task(
                            title=task_title,
                            description=task_description,
                            due_date=task_due_date
                        )
                        
                        if google_result and google_result.get('success'):
                            return f"✓ {result['message']}\n📱 Task also created in Google Tasks"
                        else:
                            return f"✓ {result['message']}\n⚠️ Note: Could not sync to Google Tasks (API may need enabling)"
                            
                    except Exception as e:
                        logger.warning(f"Failed to create Google Task: {e}")
                        return f"✓ {result['message']}\n⚠️ Note: Could not sync to Google Tasks"
                
                # Return local task creation result
                if result['success']:
                    return f"✓ {result['message']}"
                else:
                    return f"Error creating task: {result['error']}"
            
            elif any(word in message.lower() for word in ['complete', 'done', 'finish']):
                # Extract task title and complete it
                summary = self.task_manager.get_task_summary()
                pending_tasks = self.task_manager.get_pending_tasks()
                
                if pending_tasks:
                    tasks_list = "\n".join([f"- {task['title']}" for task in pending_tasks[:5]])
                    return f"You have {summary['pending']} pending tasks:\n{tasks_list}\n\nTo complete a task, say 'complete [task name]'"
                else:
                    return "You have no pending tasks! Great work."
            
            elif any(word in message.lower() for word in ['list', 'show', 'tasks']):
                summary = self.task_manager.get_task_summary()
                pending_tasks = self.task_manager.get_pending_tasks()
                overdue_tasks = self.task_manager.get_overdue_tasks()
                
                response = f"📋 Task Summary:\n"
                response += f"• {summary['pending']} pending tasks\n"
                response += f"• {summary['completed']} completed\n"
                
                if overdue_tasks:
                    response += f"• {len(overdue_tasks)} overdue\n"
                
                if pending_tasks:
                    response += f"\nNext 3 tasks:\n"
                    for task in pending_tasks[:3]:
                        priority_emoji = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
                        response += f"{priority_emoji} {task['title']}\n"
                
                return response
            
            else:
                return "I can help you create new tasks, list existing ones, or mark them complete. What would you like to do?"
                
        except Exception as e:
            logger.error(f"Error handling task request: {e}")
            return f"Error managing tasks: {str(e)}"

    def _handle_general_request(self, message):
        """Handle general conversation requests"""
        try:
            from datetime import datetime
            import pytz
            
            # Get current date and time in user's timezone
            user_tz = pytz.timezone('Europe/London')  # BST/UTC+1
            now = datetime.now(user_tz)
            today_str = now.strftime("%A, %B %d, %Y")
            current_time_str = now.strftime("%I:%M %p %Z")
            
            context = f"\n\nCurrent date and time: Today is {today_str} at {current_time_str}."
            
            if self.authenticated:
                context += "\n\nYou have access to the user's Google Calendar and Gmail services."
            else:
                context += "\n\nNote: The user hasn't connected their Google services yet. You can help them with general questions and guide them to connect Google for calendar and email features."

            # Get conversation context
            conversation_context = self.memory.get_context()
            context_str = ""
            if conversation_context:
                context_str = "\n\nPrevious conversation:\n"
                for msg in conversation_context[-4:]:  # Last 4 messages
                    context_str += f"{msg['role']}: {msg['content']}\n"

            prompt = f"""You are a helpful executive assistant. Be professional but friendly. {context}{context_str}

User message: {message}

Provide a helpful response."""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Handle different response content types properly
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            else:
                return str(response.content[0])
            
        except Exception as e:
            logger.error(f"Error handling general request: {e}")
            return "I'm here to help! Ask me about your calendar, emails, or anything else."

# Create global app instance
assistant_app = ExecutiveAssistantApp()

# Flask routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        return send_from_directory('.', 'executive_assistant.html')
    except Exception as e:
        logger.error(f"Error serving index page: {e}")
        return """
        <h1>IntelliAssist</h1>
        <p>Error loading the application. Please ensure 'executive_assistant.html' exists.</p>
        """, 500

@app.route('/api/auth/google', methods=['POST'])
def authenticate_google():
    """Initiate Google OAuth flow"""
    try:
        logger.info("Starting Google OAuth flow...")
        
        # Check if we already have valid credentials
        if assistant_app.authenticated:
            return jsonify({
                'success': True,
                'authenticated': True,
                'message': 'Already authenticated with Google'
            })
        
        # Generate OAuth URL for web-based flow
        from google_auth_oauthlib.flow import Flow
        from config import Config
        
        # Create flow for web application
        flow = Flow.from_client_secrets_file(
            'credentials/credentials.json',
            scopes=Config.GOOGLE_SCOPES
        )
        
        # Use the current domain for redirect URL
        domain = request.headers.get('Host', os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000'))
        redirect_uri = f"https://{domain}/google_callback"
        flow.redirect_uri = redirect_uri
        
        # Log the redirect URI for debugging
        logger.info(f"OAuth redirect URI: {redirect_uri}")
        
        # Generate authorization URL with account selection
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='select_account consent'
        )
        
        # Store the state in session for security
        session['oauth_state'] = state
        session['oauth_flow'] = {
            'redirect_uri': redirect_uri,
            'scopes': Config.GOOGLE_SCOPES
        }
        
        return jsonify({
            'success': True,
            'authenticated': False,
            'auth_url': authorization_url,
            'redirect_uri': redirect_uri,
            'message': 'Visit the authorization URL to complete authentication'
        })
        
    except Exception as e:
        logger.error(f"OAuth initiation error: {e}")
        return jsonify({
            'success': False,
            'authenticated': False,
            'error': f'Failed to start OAuth flow: {str(e)}'
        }), 500

@app.route('/google_callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get state from URL
        state = request.args.get('state')
        if not state:
            return "Missing OAuth state parameter. Please restart authentication.", 400
            
        # Verify state parameter for security (with fallback if session issues)
        stored_state = session.get('oauth_state')
        if stored_state and state != stored_state:
            logger.warning(f"OAuth state mismatch. Expected: {stored_state}, Got: {state}")
            return "OAuth state mismatch. Please restart authentication.", 400
        elif not stored_state:
            logger.warning(f"No stored OAuth state in session. Proceeding with OAuth completion anyway...")
            # Continue without strict state validation as fallback
            
        # Get authorization code
        code = request.args.get('code')
        if not code:
            error = request.args.get('error', 'unknown_error')
            return f"OAuth error: {error}", 400
            
        # Complete the OAuth flow
        from google_auth_oauthlib.flow import Flow
        from config import Config
        import pickle
        
        flow = Flow.from_client_secrets_file(
            'credentials/credentials.json',
            scopes=Config.GOOGLE_SCOPES
        )
        
        # Get redirect URI from session or reconstruct it
        oauth_flow = session.get('oauth_flow', {})
        if 'redirect_uri' in oauth_flow:
            flow.redirect_uri = oauth_flow['redirect_uri']
        else:
            # Fallback: reconstruct redirect URI from current request
            domain = request.headers.get('Host', os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000'))
            flow.redirect_uri = f"https://{domain}/google_callback"
            logger.info(f"Using fallback redirect URI: {flow.redirect_uri}")
        
        # Exchange code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Save credentials for future use
        with open('credentials/token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
            
        # Initialize Google services
        assistant_app.calendar_service = GoogleCalendarService(credentials)
        assistant_app.gmail_service = GmailService(credentials)
        
        if assistant_app.anthropic_client:
            assistant_app.calendar_agent = CalendarAgent(assistant_app.anthropic_client, assistant_app.calendar_service)
        
        assistant_app.authenticated = True
        
        # Clear session data
        session.pop('oauth_state', None)
        session.pop('oauth_flow', None)
        
        logger.info("✅ Google authentication completed successfully")
        
        # Return a simple HTML page that closes the popup and notifies the parent
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Complete</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .success { color: #4CAF50; font-size: 18px; }
            </style>
        </head>
        <body>
            <div class="success">
                <h2>✅ Authentication Successful!</h2>
                <p>You can close this window. Returning to IntelliAssist...</p>
            </div>
            <script>
                // Notify parent window of successful authentication
                if (window.opener) {
                    window.opener.postMessage('auth_success', '*');
                }
                // Close popup after a brief delay
                setTimeout(() => {
                    window.close();
                }, 2000);
            </script>
        </body>
        </html>
        '''
        
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return f"Authentication failed: {str(e)}", 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data"""
    try:
        data = assistant_app.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'meetings': [],
            'emails': [],
            'tasks': [],
            'stats': {'meetings': 0, 'emails': 0, 'tasks': 0, 'free_time': 0}
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat message"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400

        message = data['message'].strip()
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400

        result = assistant_app.process_chat_message(message)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get application status"""
    return jsonify({
        'authenticated': assistant_app.authenticated,
        'ai_available': assistant_app.anthropic_client is not None,
        'services': {
            'calendar': assistant_app.calendar_service is not None,
            'gmail': assistant_app.gmail_service is not None
        }
    })

@app.route('/api/smart-suggestions', methods=['GET'])
def get_smart_suggestions():
    """Generate smart suggestions based on current context"""
    try:
        if not assistant_app.anthropic_client:
            return jsonify({'success': False, 'error': 'AI not available'})
        
        suggestions = []
        current_hour = datetime.now().hour
        
        # Time-based suggestions
        if 8 <= current_hour <= 10:
            suggestions.extend([
                "Check my unread emails from yesterday",
                "What meetings do I have today?",
                "Review my priority tasks for this morning"
            ])
        elif 11 <= current_hour <= 13:
            suggestions.extend([
                "Schedule lunch meeting next week",
                "Review afternoon calendar", 
                "Send follow-up emails from morning meetings"
            ])
        elif 14 <= current_hour <= 17:
            suggestions.extend([
                "Plan tomorrow's priorities",
                "Check for urgent emails",
                "Schedule end-of-week review"
            ])
        else:
            suggestions.extend([
                "Review today's accomplishments",
                "Prepare agenda for tomorrow",
                "Schedule follow-up tasks"
            ])
        
        # Add task-related suggestions
        try:
            from task_manager import TaskManager
            if not hasattr(assistant_app, 'task_manager'):
                assistant_app.task_manager = TaskManager(assistant_app.anthropic_client)
            
            task_summary = assistant_app.task_manager.get_task_summary()
            if task_summary['overdue'] > 0:
                suggestions.insert(0, f"Review {task_summary['overdue']} overdue tasks")
            if task_summary['due_today'] > 0:
                suggestions.insert(0, f"Complete {task_summary['due_today']} tasks due today")
        except Exception as e:
            logger.warning(f"Could not load task suggestions: {e}")
        
        return jsonify({
            'success': True, 
            'suggestions': suggestions[:4]
        })
        
    except Exception as e:
        logger.error(f"Error generating smart suggestions: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get priority tasks"""
    try:
        if not hasattr(assistant_app, 'task_manager'):
            from task_manager import TaskManager
            assistant_app.task_manager = TaskManager(assistant_app.anthropic_client)
        
        pending_tasks = assistant_app.task_manager.get_pending_tasks()
        
        # Convert to format expected by frontend
        tasks_data = []
        for task in pending_tasks:
            tasks_data.append({
                'title': task.get('title', ''),
                'priority': task.get('priority', 'Medium'),
                'due_date': task.get('due_date'),
                'description': task.get('description', ''),
                'completed': task.get('completed', False)
            })
        
        return jsonify({'success': True, 'tasks': tasks_data})
        
    except Exception as e:
        logger.error(f"Tasks endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/complete', methods=['POST'])
def complete_task():
    """Mark a task as completed"""
    try:
        data = request.get_json()
        task_title = data.get('title')
        
        if not task_title:
            return jsonify({'success': False, 'error': 'Task title required'})
        
        if not hasattr(assistant_app, 'task_manager'):
            from task_manager import TaskManager
            assistant_app.task_manager = TaskManager(assistant_app.anthropic_client)
        
        result = assistant_app.task_manager.complete_task(task_title)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Complete task error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/delete', methods=['POST'])
def delete_task():
    """Delete a Google Task"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({'success': False, 'error': 'Task ID required'})
        
        if not assistant_app.authenticated or not assistant_app.tasks_service:
            return jsonify({'success': False, 'error': 'Google Tasks not available'})
        
        # Delete the task using Google Tasks API
        assistant_app.tasks_service.delete_task(task_id)
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Delete task error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/emails/delete', methods=['POST'])
def delete_email():
    """Delete an email (move to trash)"""
    try:
        data = request.get_json()
        email_id = data.get('email_id')
        
        if not email_id:
            return jsonify({'success': False, 'error': 'Email ID required'})
        
        if not assistant_app.authenticated or not assistant_app.gmail_service:
            return jsonify({'success': False, 'error': 'Gmail not available'})
        
        # Delete the email using Gmail API
        assistant_app.gmail_service.delete_message(email_id)
        
        return jsonify({
            'success': True,
            'message': 'Email moved to trash successfully'
        })
        
    except Exception as e:
        logger.error(f"Delete email error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/meetings/delete', methods=['POST'])
def delete_meeting():
    """Delete a calendar meeting"""
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        
        if not event_id:
            return jsonify({'success': False, 'error': 'Event ID required'})
        
        if not assistant_app.authenticated or not assistant_app.calendar_service:
            return jsonify({'success': False, 'error': 'Google Calendar not available'})
        
        # Delete the event using Google Calendar API
        assistant_app.calendar_service.delete_event(event_id)
        
        return jsonify({
            'success': True,
            'message': 'Meeting deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Delete meeting error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/priority-emails', methods=['GET'])
def get_priority_emails():
    """Get priority emails based on AI analysis"""
    try:
        if not assistant_app.authenticated or not assistant_app.gmail_service:
            # Return mock priority emails for demo when not connected
            mock_emails = [
                {
                    'subject': 'Urgent: Project Deadline Update',
                    'sender': 'project.manager@company.com',
                    'timestamp': datetime.now().isoformat(),
                    'priority': 'Urgent',
                    'gmail_id': 'mock_1'
                },
                {
                    'subject': 'Important: Client Meeting Rescheduled',
                    'sender': 'client.relations@company.com',
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'priority': 'Important',
                    'gmail_id': 'mock_2'
                },
                {
                    'subject': 'New Budget Proposal for Review',
                    'sender': 'finance@company.com',
                    'timestamp': (datetime.now() - timedelta(hours=4)).isoformat(),
                    'priority': 'Important',
                    'gmail_id': 'mock_3'
                }
            ]
            return jsonify({'success': True, 'emails': mock_emails})
        
        # Get recent emails
        emails = assistant_app.gmail_service.get_messages('is:unread', max_results=20)
        
        # Use AI to analyze and prioritize emails
        priority_emails = []
        if assistant_app.anthropic_client and emails:
            from task_manager import EmailInsightAgent
            if not hasattr(assistant_app, 'email_agent'):
                assistant_app.email_agent = EmailInsightAgent(
                    assistant_app.anthropic_client, 
                    assistant_app.gmail_service
                )
            
            analysis = assistant_app.email_agent.analyze_emails(emails)
            priority_emails = analysis.get('priority_emails', [])
        
        return jsonify({'success': True, 'emails': priority_emails})
        
    except Exception as e:
        logger.error(f"Priority emails endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/disconnect', methods=['POST'])
def disconnect_google():
    """Disconnect from Google services"""
    try:
        # Clear authentication state
        assistant_app.authenticated = False
        assistant_app.calendar_service = None
        assistant_app.gmail_service = None
        assistant_app.tasks_service = None
        assistant_app.calendar_agent = None
        
        # Remove token file
        import os
        token_file = 'credentials/token.pickle'
        if os.path.exists(token_file):
            os.remove(token_file)
            logger.info("Authentication tokens cleared")
        
        return jsonify({'success': True, 'message': 'Successfully disconnected from Google services'})
        
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/create-task', methods=['POST'])
def create_google_task():
    """Create a new Google Task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        title = data.get('title', '').strip()
        if not title:
            return jsonify({'success': False, 'error': 'Task title is required'})
        
        description = data.get('description', '').strip()
        due_date = data.get('due_date')
        
        # Check if Google Tasks service is available
        if not assistant_app.tasks_service:
            return jsonify({
                'success': False, 
                'error': 'Google Tasks API not available. Please ensure you are authenticated with Google.',
                'action_required': 'reconnect'
            })
        
        # Create the task in Google Tasks
        try:
            result = assistant_app.tasks_service.create_task(
                title=title,
                description=description,
                due_date=due_date
            )
            
            if result and result.get('success'):
                return jsonify({
                    'success': True, 
                    'message': f'Task "{title}" created successfully in Google Tasks',
                    'task_id': result.get('task_id')
                })
            else:
                error_msg = result.get('error', 'Failed to create task') if result else 'Failed to create task'
                return jsonify({
                    'success': False, 
                    'error': f'Google Tasks error: {error_msg}',
                    'action_required': 'enable_api'
                })
        except Exception as e:
            logger.error(f"Google Tasks API error: {e}")
            if "accessNotConfigured" in str(e) or "API has not been used" in str(e):
                return jsonify({
                    'success': False, 
                    'error': 'Google Tasks API is not enabled in your Google Cloud project.',
                    'action_required': 'enable_api',
                    'instructions': 'Go to https://console.developers.google.com/apis/api/tasks.googleapis.com/overview and enable the Google Tasks API'
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Google Tasks API error: {str(e)}',
                    'action_required': 'retry'
                })
            
    except Exception as e:
        logger.error(f"Create task endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-tasks')
def test_tasks():
    """Test Google Tasks API directly"""
    debug_info = {
        'authenticated': assistant_app.authenticated,
        'tasks_service_exists': assistant_app.tasks_service is not None,
        'calendar_service_exists': assistant_app.calendar_service is not None,
        'gmail_service_exists': assistant_app.gmail_service is not None
    }
    
    logger.info(f"🔧 Debug info: {debug_info}")
    
    try:
        if not assistant_app.authenticated:
            return jsonify({'error': 'Not authenticated', 'debug': debug_info})
            
        if not assistant_app.tasks_service:
            return jsonify({'error': 'Tasks service not available', 'debug': debug_info})
        
        logger.info("🔧 Testing Google Tasks API...")
        
        # Test basic API access
        task_lists = assistant_app.tasks_service.get_task_lists()
        logger.info(f"Task lists found: {len(task_lists)}")
        
        # Get all tasks
        all_tasks = assistant_app.tasks_service.get_tasks()
        logger.info(f"Total tasks found: {len(all_tasks)}")
        
        # Get today's tasks
        todays_tasks = assistant_app.tasks_service.get_todays_tasks()
        logger.info(f"Today's tasks found: {len(todays_tasks)}")
        
        return jsonify({
            'success': True,
            'task_lists': len(task_lists),
            'total_tasks': len(all_tasks),
            'todays_tasks': len(todays_tasks),
            'task_details': [{'title': t.title, 'due_date': str(t.due_date)} for t in todays_tasks[:5]],
            'debug': debug_info
        })
        
    except Exception as e:
        logger.error(f"Tasks API test failed: {e}")
        return jsonify({'error': str(e), 'debug': debug_info})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Executive Assistant application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
