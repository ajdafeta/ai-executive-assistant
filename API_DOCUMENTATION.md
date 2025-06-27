# IntelliAssist API Documentation

## Endpoints Overview

IntelliAssist provides a RESTful API interface for managing emails, calendar events, and tasks through Google services integration.

## Authentication Endpoints

### `GET /`
**Description**: Serves the main application interface
- **Returns**: HTML dashboard page
- **Authentication**: Optional (redirects to login if not authenticated)

### `GET /authenticate/google`
**Description**: Initiates Google OAuth authentication flow
- **Returns**: Redirect to Google OAuth consent screen
- **Parameters**: None
- **Response**: HTTP redirect to Google authorization

### `GET /google/callback`
**Description**: Handles Google OAuth callback after user consent
- **Returns**: JSON status of authentication
- **Parameters**: 
  - `code` (query): OAuth authorization code
  - `state` (query): CSRF protection token

### `GET /status`
**Description**: Check current authentication status
- **Returns**: 
  ```json
  {
    "authenticated": true/false,
    "services": ["gmail", "calendar", "tasks"]
  }
  ```

### `POST /disconnect`
**Description**: Disconnect from Google services
- **Returns**: JSON confirmation of disconnection
- **Side Effects**: Removes stored credentials

## Dashboard Data Endpoints

### `GET /api/dashboard`
**Description**: Retrieve comprehensive dashboard data
- **Returns**:
  ```json
  {
    "authenticated": true,
    "meetings": [
      {
        "title": "Meeting Title",
        "date": "2025-06-27T18:00:00Z",
        "attendees": ["user@example.com"],
        "location": "Conference Room A"
      }
    ],
    "emails": [
      {
        "gmail_id": "abc123",
        "subject": "Email Subject",
        "sender": "sender@example.com",
        "time": "10:30",
        "priority": "Normal",
        "read": false
      }
    ],
    "tasks": [
      {
        "task_id": "task123",
        "title": "Task Title",
        "due_date": "2025-06-28",
        "completed": false,
        "source": "google_tasks"
      }
    ],
    "stats": {
      "meetings": 3,
      "emails": 10,
      "tasks": 5,
      "free_time": "2.5h available"
    }
  }
  ```

### `GET /api/smart-suggestions`
**Description**: Get AI-generated contextual suggestions
- **Returns**:
  ```json
  {
    "suggestions": [
      {
        "type": "calendar",
        "text": "Schedule follow-up meeting for Project Alpha",
        "priority": "high",
        "action": "create_meeting"
      }
    ]
  }
  ```

## Task Management Endpoints

### `GET /api/tasks`
**Description**: Retrieve all Google Tasks
- **Returns**: Array of task objects with Google Tasks data
- **Parameters**: 
  - `include_completed` (optional): Include completed tasks

### `POST /api/tasks`
**Description**: Create a new Google Task
- **Body**:
  ```json
  {
    "title": "Task Title",
    "description": "Task Description",
    "due_date": "2025-06-28"
  }
  ```
- **Returns**: Created task object with Google Task ID

### `POST /api/tasks/complete`
**Description**: Mark a task as completed
- **Body**:
  ```json
  {
    "task_id": "google_task_id_here"
  }
  ```
- **Returns**: Updated task status

### `DELETE /api/tasks/<task_id>`
**Description**: Delete a Google Task
- **Parameters**: 
  - `task_id`: Google Tasks API task identifier
- **Returns**: Deletion confirmation

## Email Management Endpoints

### `GET /api/emails/priority`
**Description**: Get priority emails based on AI analysis
- **Returns**: Array of high-priority email objects
- **Parameters**:
  - `max_results` (optional): Maximum number of emails to return

### `DELETE /api/emails/<gmail_id>`
**Description**: Delete an email (move to trash)
- **Parameters**:
  - `gmail_id`: Gmail message identifier
- **Returns**: Deletion confirmation

## Calendar Management Endpoints

### `DELETE /api/meetings/<event_id>`
**Description**: Delete a calendar event
- **Parameters**:
  - `event_id`: Google Calendar event identifier
- **Returns**: Deletion confirmation

## Chat and AI Endpoints

### `POST /api/chat`
**Description**: Process natural language requests through AI
- **Body**:
  ```json
  {
    "message": "Schedule a meeting with John tomorrow at 2 PM"
  }
  ```
- **Returns**:
  ```json
  {
    "response": "I've scheduled a meeting with John for tomorrow at 2:00 PM. The calendar event has been created.",
    "actions_taken": ["create_calendar_event"],
    "data": {
      "event_id": "calendar_event_id"
    }
  }
  ```

## Data Models

### Task Object
```json
{
  "task_id": "string",
  "title": "string",
  "description": "string",
  "due_date": "YYYY-MM-DD",
  "completed": boolean,
  "created_at": "ISO 8601 datetime",
  "priority": "High|Medium|Low",
  "source": "google_tasks"
}
```

### Email Object
```json
{
  "gmail_id": "string",
  "subject": "string",
  "sender": "string",
  "content": "string",
  "timestamp": "ISO 8601 datetime",
  "priority": "High|Medium|Normal",
  "read": boolean,
  "thread_id": "string"
}
```

### Meeting Object
```json
{
  "google_event_id": "string",
  "title": "string",
  "date": "ISO 8601 datetime",
  "attendees": ["email1", "email2"],
  "agenda": "string",
  "duration": "integer (minutes)",
  "location": "string",
  "status": "scheduled|completed|cancelled"
}
```

## Error Responses

### Authentication Errors
```json
{
  "error": "authentication_required",
  "message": "Please authenticate with Google services",
  "redirect": "/authenticate/google"
}
```

### API Errors
```json
{
  "error": "api_error",
  "message": "Failed to connect to Google Calendar API",
  "details": "Quota exceeded or service unavailable"
}
```

### Validation Errors
```json
{
  "error": "validation_error",
  "message": "Invalid task data provided",
  "fields": ["title", "due_date"]
}
```

## Rate Limits

- **Google APIs**: Subject to Google's API quotas
- **Chat API**: Limited by Anthropic API usage
- **Dashboard Updates**: Auto-refresh every 10 seconds
- **Bulk Operations**: Maximum 50 items per request

## Response Codes

- `200`: Success
- `201`: Created (for new resources)
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

## Usage Examples

### Creating a Task via Chat
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to review quarterly reports due next Friday"}'
```

### Getting Dashboard Data
```bash
curl -X GET http://localhost:5000/api/dashboard \
  -H "Accept: application/json"
```

### Deleting an Email
```bash
curl -X DELETE http://localhost:5000/api/emails/gmail_message_id_here
```

## Integration Notes

- All datetime values are in ISO 8601 format with UTC timezone
- Google service integration requires proper OAuth scopes
- AI features require valid Anthropic API key
- Session management uses secure cookies for authentication state
- CORS is configured for cross-origin requests in development

## Security Considerations

- OAuth tokens are encrypted and stored securely
- API keys are managed through environment variables
- Session timeouts prevent unauthorized access
- Input validation prevents injection attacks
- HTTPS required for production deployments