"""
Hugging Face Spaces entry point for RezScan backend.
This file is used by Hugging Face Spaces to run the Flask application.
"""
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Import the Flask app
from api.main import app

# Hugging Face Spaces runs the app automatically if it's named 'app'
# The app is already configured in api/main.py to use PORT env var and 0.0.0.0
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)

