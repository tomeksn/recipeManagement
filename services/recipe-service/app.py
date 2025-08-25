"""Main application entry point for the Recipe Service."""
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)