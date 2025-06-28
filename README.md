# IntelliAssist

An AI-powered executive assistant web application that seamlessly integrates Google services for comprehensive email, calendar, and task management with advanced conversational intelligence.

![Exectutive Assistant](https://img.shields.io/badge/AI-Claude%20Sonnet%204-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![License](https://img.shields.io/badge/License-Apache2.0-yellow)

## 🌟 Features

### Email Management
- **Smart Email Analysis**: AI-powered email prioritization and insights
- **Natural Language Email Composition**: Send emails by describing what you want to say
- **Unread Email Monitoring**: Real-time tracking of important messages
- **Email Actions**: Delete, archive, and manage emails through conversation

### Calendar Intelligence
- **Conversational Meeting Scheduling**: "Schedule a team meeting tomorrow at 2 PM"
- **Smart Time Finding**: Automatically find free slots in your schedule
- **Meeting Management**: View, modify, and delete calendar events
- **Today's Schedule**: Quick access to current day's meetings with full details

### Task Management
- **Google Tasks Integration**: Seamlessly work with your existing Google Tasks
- **AI Task Creation**: Convert natural language into structured tasks
- **Task Completion Tracking**: Mark tasks complete with conversation
- **Priority-based Organization**: Visual indicators for task importance

### Conversational AI
- **Context-Aware Conversations**: Remembers previous interactions
- **Natural Language Processing**: Powered by Claude 4.0 Sonnet
- **Smart Suggestions**: Contextual recommendations based on your schedule
- **Multi-turn Dialogues**: Follow-up questions and clarifications

### Dashboard & UI
- **Real-time Updates**: Live data refresh every 10 seconds
- **Modern Interface**: Clean, responsive design with intuitive navigation
- **Quick Actions**: One-click access to common tasks
- **Visual Indicators**: Color-coded priorities and status markers

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/intelliassist.git
cd intelliassist

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your API keys

# Run the application
python main.py
```

Visit `http://localhost:5000` and connect your Google account to get started!

## 🛠 Tech Stack

**Backend:**
- **Python Flask**: Web framework with CORS support
- **Claude 4.0 Sonnet**: Advanced AI for natural language processing
- **Google APIs**: Gmail, Calendar, and Tasks integration
- **Google OAuth 2.0**: Secure authentication flow
- **Gunicorn**: Production WSGI server

**Frontend:**
- **Modern Web Stack**: HTML5, CSS3, Vanilla JavaScript
- **Responsive Design**: Mobile-first approach with card-based UI
- **Font Awesome**: Professional icon library
- **Real-time Updates**: Auto-refreshing data every 10 seconds

## 📖 Documentation

- **[📚 Capabilities](CAPABILITIES.md)**: Comprehensive overview of all features and functionalities
- **[⚙️ Setup Guide](SETUP.md)**: Detailed installation and configuration instructions
- **[🔌 API Documentation](API_DOCUMENTATION.md)**: Complete API reference for developers
- **[🛠 Technical Architecture](replit.md)**: System architecture and technical decisions

## 🚀 Quick Setup

### Prerequisites
- Python 3.11+
- Google Cloud Platform account with Gmail, Calendar, and Tasks APIs enabled
- Anthropic API key

### One-Minute Setup

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/intelliassist.git
cd intelliassist

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.template .env
# Edit .env with your API keys

# 4. Set up Google OAuth credentials
# Place your credentials.json in credentials/ directory

# 5. Run the application
python main.py
```

**🌐 Visit `http://localhost:5000` and connect your Google account!**

For detailed setup instructions, see [SETUP.md](SETUP.md).

## 💡 Usage Examples

**Natural Language Interactions:**
- "Schedule a team meeting tomorrow at 2 PM with alice@company.com"
- "What meetings do I have today?"
- "Create a task to review quarterly reports by Friday"
- "Send an email to john@company.com about the project update"
- "When is my next free time?"

## 🏗 Architecture

### Core Components
- **GoogleAuthManager**: Secure OAuth authentication flow
- **GoogleCalendarService**: Calendar operations and scheduling
- **GmailService**: Email management and composition
- **GoogleTasksService**: Task creation and tracking
- **CalendarAgent**: AI-powered meeting intelligence
- **ContextMemory**: Conversation history and context

### Tech Stack
- **Backend**: Flask, Python 3.11, Gunicorn
- **AI**: Claude 4.0 Sonnet (Anthropic)
- **APIs**: Google Gmail, Calendar, Tasks
- **Auth**: Google OAuth 2.0
- **Frontend**: Modern HTML5/CSS3/JavaScript

## 🔒 Security

- **Secure Authentication**: Google OAuth 2.0 with encrypted token storage
- **Environment Protection**: All API keys managed via environment variables
- **Session Security**: Configurable session secrets and timeouts
- **Data Privacy**: No local data storage, direct API integration only

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🚦 Roadmap      

-

---
