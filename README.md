# IntelliAssist

An AI-powered executive assistant web application that seamlessly integrates Google services for comprehensive email, calendar, and task management. Built with Claude Sonnet 4 and Replit.

![Executive Assistant](https://img.shields.io/badge/AI-Claude%20Sonnet%204-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Smart Email Management**: View, prioritise, and manage Gmail messages with AI-powered insights
- **Intelligent Calendar**: Schedule meetings, find free time slots, and manage calendar events
- **Task Automation**: Create, track, and complete tasks with Google Tasks integration
- **Natural Language Processing**: Interact with your assistant using conversational language
- **Real-time Dashboard**: Auto-refreshing dashboard with live data from Google services
- **Google OAuth Integration**: Secure authentication with Gmail, Calendar, and Tasks APIs

## Tech Stack

**Backend:**
- Python Flask web framework
- Claude API (Sonnet 4) for AI processing
- Google APIs (Gmail, Calendar, Tasks)
- Google OAuth 2.0 authentication
- Gunicorn WSGI server

**Frontend:**
- HTML5, CSS3, JavaScript
- Responsive design with modern card-based UI
- Font Awesome icons
- Real-time data updates

## Setup Instructions

### Prerequisites
- Python 3.11+
- Google Cloud Platform account
- Anthropic API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/intelliassist.git
   cd intelliassist
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google OAuth:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create a new OAuth 2.0 Client ID
   - Add your domain to Authorised redirect URIs
   - Download credentials and save as `credentials/credentials.json`

4. **Configure environment variables:**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

## Environment Variables

Create a `.env` file with:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SESSION_SECRET=your_session_secret
```

## Usage

1. Navigate to the application URL
2. Click "Connect Google Account" to authenticate
3. Grant permissions for Gmail, Calendar, and Tasks
4. Use the dashboard to view your data
5. Interact with the AI assistant using natural language

## Key Components

- **GoogleAuthManager**: Handles OAuth authentication flow
- **GoogleCalendarService**: Manages calendar operations
- **GmailService**: Handles email operations
- **GoogleTasksService**: Manages task operations
- **CalendarAgent**: AI-powered calendar management
- **ContextMemory**: Maintains conversation context

## Security

- All API keys stored securely in environment variables
- Google OAuth credentials managed through secure flow
- Session management with configurable secrets
- CORS configured for cross-origin requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Apache 2.0 - see LICENSE file for details

## Support

For issues and questions, please open a GitHub issue or contact the development team.
