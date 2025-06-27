# IntelliAssist

## Overview

This is a Google-integrated AI-powered assistant application built with Flask and Python. IntelliAssist provides intelligent assistance for managing tasks, meetings, and emails through Google's APIs (Gmail and Google Calendar) with Claude AI integration for intelligent automation.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with CORS support
- **AI Integration**: Anthropic's Claude API for intelligent processing
- **Authentication**: Google OAuth 2.0 for accessing Google services
- **Deployment**: Gunicorn WSGI server with autoscale deployment target

### Frontend Architecture
- **Type**: Single-page HTML application with vanilla JavaScript
- **Styling**: CSS with CSS custom properties for theming
- **Icons**: Font Awesome for UI icons
- **Layout**: Responsive design with modern card-based UI

## Key Components

### Core Services
1. **GoogleAuthManager**: Handles OAuth authentication flow with Google
2. **GoogleCalendarService**: Manages calendar operations and event creation
3. **GmailService**: Handles email reading, sending, and management
4. **CalendarAgent**: AI-powered calendar management with Claude integration
5. **ContextMemory**: Maintains conversation context and user preferences

### Data Models
- **Task**: Task management with priority, due dates, and completion status
- **Meeting**: Meeting scheduling with attendees, agenda, and Google Calendar integration
- **Email**: Email handling with sender, recipient, and content management

### Configuration Management
- **Config Class**: Centralized configuration with environment variable validation
- **Environment Variables**: Secure handling of API keys and application settings
- **Google Scopes**: Comprehensive Gmail and Calendar permissions

## Data Flow

1. **Authentication Flow**:
   - User initiates Google OAuth through the web interface
   - Credentials stored securely in local pickle files
   - Services initialized with authenticated credentials

2. **AI Processing**:
   - User requests processed through Claude API
   - Context maintained in memory for conversation continuity
   - Responses formatted for web interface display

3. **Google Integration**:
   - Calendar events created/modified through Google Calendar API
   - Emails sent/received through Gmail API
   - Real-time synchronization with Google services

## External Dependencies

### Required APIs
- **Anthropic Claude API**: AI processing and natural language understanding
- **Google Calendar API**: Calendar management and event scheduling
- **Gmail API**: Email operations and management

### Python Packages
- **flask**: Web framework and routing
- **anthropic**: Claude AI client library
- **google-api-python-client**: Google services integration
- **google-auth**: Authentication and authorization
- **pandas**: Data manipulation and analysis
- **python-dateutil**: Date and time parsing
- **pytz**: Timezone handling

## Deployment Strategy

### Production Deployment
- **Server**: Gunicorn WSGI server with auto-scaling
- **Environment**: Nix-based environment with Python 3.11
- **Port Configuration**: Bound to 0.0.0.0:5000
- **SSL**: HTTPS support through deployment platform

### Development Setup
- **Local Server**: Flask development server with debug mode
- **Hot Reload**: Automatic reloading on code changes
- **Environment**: Development environment variables

### Security Considerations
- Session secrets configurable via environment variables
- API keys stored securely in environment variables
- Google OAuth credentials managed through secure flow
- CORS configured for cross-origin requests

## Recent Changes

### June 27, 2025 - Cleaned Task Management System
- **Authentic Data Only**: Removed local task storage to display only Google Tasks from user's account
- **Streamlined Interface**: Eliminated duplicate tasks from local storage file (data/tasks.json)
- **Google Tasks Integration**: All task operations now work exclusively with Google Tasks API
- **Data Integrity**: Ensured authentic task data with proper Google Task IDs for deletion functionality

### June 26, 2025 - Enhanced IntelliAssist Features
- **Smart Task Management**: Added AI-powered task creation, tracking, and completion with priority-based sorting
- **Intelligent Suggestions**: Implemented time-based smart suggestions that adapt to user's schedule and context
- **Enhanced UI**: Improved quick action buttons with icons and better visual organization
- **Calendar Integration**: Enhanced calendar agent with smart scheduling and meeting management
- **Email Insights**: Added email analysis and response suggestion capabilities
- **Task Dashboard**: Integrated task statistics into main dashboard display
- **Error Handling**: Improved error handling and user feedback throughout the application
- **Comprehensive Calendar Visibility**: Enhanced calendar agent with full schedule visibility, detailed event information including duration and attendees, and intelligent free time slot analysis across multiple days

### Technical Improvements
- Created comprehensive TaskManager class with AI-powered natural language task parsing
- Added SmartSchedulingAgent for intelligent meeting time suggestions
- Implemented EmailInsightAgent for automated email analysis
- Enhanced frontend with smart suggestions display and improved user interactions
- Added /api/smart-suggestions endpoint for contextual recommendations
- **Rebranding**: Changed from "Executive Assistant" to "IntelliAssist" with new AI-themed animated logo
- **Web OAuth Flow**: Implemented proper web-based Google authentication with popup window and automatic polling

## Changelog

- June 26, 2025. Initial setup and comprehensive feature enhancement

## User Preferences

Preferred communication style: Simple, everyday language.