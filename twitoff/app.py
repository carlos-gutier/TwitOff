"""Main application and routing logic for TwitOff."""
from flask import Flask

def create_app():
    """Create and configure and instance of the Flask application"""
    app = Flask(__name__)

    @app.route('/')
    def root():
        return 'Welcome to TwitOff!!'
    return app
