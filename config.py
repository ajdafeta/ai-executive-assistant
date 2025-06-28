import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    DEBUG = True
    
    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Anthropic API configuration
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    
    # Google API Scopes
    GOOGLE_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/tasks'
    ]
    
    # Timezone configuration
    DEFAULT_TIMEZONE = 'Europe/London'
    
    @staticmethod
    def validate_config():
        """Validate that required configuration is present"""
        errors = []
        
        if not Config.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY environment variable is required")
            
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))
        
        return True
