"""Calculator Service Application Entry Point."""
import os
from flask import Flask
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Development server
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8003)),
        debug=debug
    )