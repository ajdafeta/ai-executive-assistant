# IntelliAssist Setup Guide

This guide will walk you through setting up IntelliAssist on your local machine or server.

## Prerequisites

- Python 3.11 or higher
- Google Cloud Platform account
- Anthropic API account
- Modern web browser

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/intelliassist.git
cd intelliassist
```

### 2. Set Up Python Environment

```bash
# Create virtual environment (recommended)
python -m venv intelliassist-env
source intelliassist-env/bin/activate  # On Windows: intelliassist-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Google Cloud Platform Setup

#### Create a New Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID for later use

#### Enable Required APIs
Enable these APIs in your Google Cloud project:
- Gmail API
- Google Calendar API
- Google Tasks API

```bash
# Using gcloud CLI (optional)
gcloud services enable gmail.googleapis.com
gcloud services enable calendar-json.googleapis.com
gcloud services enable tasks.googleapis.com
```

#### Create OAuth 2.0 Credentials
1. Navigate to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth 2.0 Client IDs**
3. Set application type to **Web application**
4. Add authorized redirect URIs:
   - `http://localhost:5000/google/callback` (for development)
   - `https://yourdomain.com/google/callback` (for production)
5. Download the credentials JSON file
6. Save it as `credentials/credentials.json` in your project directory

### 4. Anthropic API Setup

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Generate an API key
4. Note the key for environment configuration

### 5. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.template .env
```

Edit the `.env` file with your credentials:

```env
# Anthropic AI
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google OAuth (from credentials.json)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Session Security
SESSION_SECRET=your_random_session_secret_key

# Optional: Timezone (defaults to Europe/London)
DEFAULT_TIMEZONE=Europe/London
```

### 6. Directory Setup

Create required directories:

```bash
mkdir -p credentials
mkdir -p data
```

Ensure your project structure looks like this:

```
intelliassist/
├── credentials/
│   └── credentials.json
├── data/
├── .env
├── .env.template
├── app.py
├── main.py
├── run_assistant.py
├── google_backend.py
├── models.py
├── config.py
├── executive_assistant.html
└── README.md
```

### 7. Test the Installation

Run the application:

```bash
python main.py
```

You should see output similar to:

```
INFO:run_assistant:✅ Anthropic client initialized successfully
INFO:run_assistant:🚀 IntelliAssist starting up...
[2025-06-28 18:00:00 +0000] [12345] [INFO] Starting gunicorn 21.2.0
[2025-06-28 18:00:00 +0000] [12345] [INFO] Listening at: http://0.0.0.0:5000
```

### 8. First-Time Authentication

1. Open your browser and navigate to `http://localhost:5000`
2. Click **Connect Google Account**
3. Complete the Google OAuth flow
4. Grant permissions for Gmail, Calendar, and Tasks
5. You should be redirected back to the dashboard

## Troubleshooting

### Common Issues

**OAuth Redirect URI Mismatch**
- Ensure your redirect URIs in Google Console match exactly
- Check for trailing slashes or HTTP vs HTTPS mismatches

**API Key Issues**
- Verify your Anthropic API key is valid and has sufficient credits
- Check that Google APIs are enabled for your project

**Permission Errors**
- Ensure the application has proper Google API scopes
- Check that your OAuth app is not in testing mode for production use

**Port Already in Use**
- Change the port in `main.py` if 5000 is occupied
- Update redirect URIs accordingly

### Logs and Debugging

Enable debug logging by setting in your `.env`:

```env
DEBUG=True
```

Check logs for detailed error information:

```bash
# View real-time logs
tail -f logs/intelliassist.log
```

### Google API Quotas

Monitor your API usage in Google Cloud Console:
- Gmail API: 1 billion quota units per day
- Calendar API: 1 million requests per day
- Tasks API: 50,000 requests per day

## Production Deployment

### Environment Variables

For production, set these additional variables:

```env
DEBUG=False
SESSION_SECRET=strong_random_key_for_production
REPLIT_DEV_DOMAIN=yourdomain.com
```

### Security Considerations

1. **HTTPS Required**: Use HTTPS in production
2. **Secure Session Keys**: Generate strong random session secrets
3. **API Key Security**: Never commit API keys to version control
4. **OAuth Configuration**: Update redirect URIs for production domain

### Web Server Setup

For production deployment with Gunicorn:

```bash
# Install Gunicorn if not already installed
pip install gunicorn

# Run with production settings
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

### Reverse Proxy Setup (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [API documentation](API_DOCUMENTATION.md)
3. Open an issue on GitHub with:
   - Error messages
   - Steps to reproduce
   - Your environment details

## Next Steps

- Read the [Capabilities Documentation](CAPABILITIES.md)
- Explore the [API Documentation](API_DOCUMENTATION.md)
- Customize the interface to your needs
- Set up monitoring and logging for production use