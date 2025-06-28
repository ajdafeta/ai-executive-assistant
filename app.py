import os
import logging
from flask import Flask
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure app
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.config['DEBUG'] = True

# Import routes after app creation to avoid circular imports
from run_assistant import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
