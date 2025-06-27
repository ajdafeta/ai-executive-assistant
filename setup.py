#!/usr/bin/env python3
"""
Setup script for Executive Assistant
This script helps you set up the Google Executive Assistant application.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

def check_python_version():
    """Check if Python version is 3.7+"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required. You have:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])
    return True

def install_requirements():
    """Install required Python packages"""
    packages = [
        'flask>=2.3.0',
        'flask-cors>=4.0.0',
        'google-auth>=2.23.0',
        'google-auth-oauthlib>=1.1.0',
        'google-auth-httplib2>=0.1.1',
        'google-api-python-client>=2.103.0',
        'anthropic>=0.7.0',
        'pandas>=2.1.0',
        'python-dateutil>=2.8.0',
        'python-dotenv>=1.0.0',
        'pytz>=2023.3'
    ]

    print("📦 Installing required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['credentials']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_credentials():
    """Check if Google credentials file exists"""
    credentials_path = Path('credentials/credentials.json')
    
    if credentials_path.exists():
        print("✅ credentials.json found")
        return True
    else:
        print("❌ credentials.json not found")
        print("\n🔧 To get Google credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Gmail API and Calendar API")
        print("4. Go to 'Credentials' > 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("5. Choose 'Desktop application'")
        print("6. Download the JSON file and rename it to 'credentials.json'")
        print("7. Place it in the 'credentials/' directory")
        return False

def check_anthropic_key():
    """Check if Anthropic API key is set"""
    load_dotenv()
    
    if os.getenv('ANTHROPIC_API_KEY'):
        print("✅ ANTHROPIC_API_KEY is set")
        return True
    else:
        print("❌ ANTHROPIC_API_KEY not set")
        print("\n🔧 To get Anthropic API key:")
        print("1. Go to https://console.anthropic.com/")
        print("2. Create an account or sign in")
        print("3. Go to API Keys section")
        print("4. Create a new API key")
        print("5. Add it to your .env file: ANTHROPIC_API_KEY=your_key_here")
        return False

def create_env_file():
    """Create a .env file template"""
    env_content = """# Environment variables for Executive Assistant

# Anthropic API Key (Required)
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Flask Configuration
SESSION_SECRET=your-secret-key-here-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Google OAuth (Optional - for future web OAuth)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Timezone Configuration (Optional)
DEFAULT_TIMEZONE=UTC
"""

    env_path = Path('.env')
    
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("   Please edit .env file and add your API keys")
    else:
        print("✅ .env file already exists")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Environment variables
.env

# Google credentials and tokens
credentials/
*.pickle

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
    
    gitignore_path = Path('.gitignore')
    
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")

def validate_files():
    """Validate that all required files exist"""
    required_files = [
        'main.py',
        'app.py',
        'run_assistant.py',
        'google_backend.py',
        'executive_assistant.html',
        'config.py',
        'models.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required application files found")
    return True

def main():
    """Main setup function"""
    print("🤖 Executive Assistant Setup")
    print("=" * 40)

    # Check Python version
    if not check_python_version():
        return False

    # Install packages
    if not install_requirements():
        print("❌ Failed to install some packages. Please install manually.")
        return False

    # Create directories
    create_directories()

    # Create configuration files
    create_env_file()
    create_gitignore()

    # Validate application files
    files_ok = validate_files()

    # Check credentials
    creds_ok = check_credentials()

    # Check API key
    key_ok = check_anthropic_key()

    print("\n" + "=" * 40)
    print("📋 Setup Summary:")

    if files_ok and creds_ok and key_ok:
        print("✅ Everything is ready!")
        print("\n🚀 To start the application:")
        print("   python main.py")
        print("\n🌐 Then open: http://localhost:5000")
    else:
        print("⚠️  Setup incomplete. Please:")
        if not files_ok:
            print("   - Ensure all application files are present")
        if not creds_ok:
            print("   - Add credentials.json file to credentials/ directory")
        if not key_ok:
            print("   - Set ANTHROPIC_API_KEY in .env file")
        print("\nThen run: python main.py")

    print("\n📚 Documentation:")
    print("   - Google API setup: https://console.cloud.google.com/")
    print("   - Anthropic API: https://console.anthropic.com/")
    print("   - Application will run on: http://localhost:5000")

    return True

if __name__ == '__main__':
    main()
