"""Main application entry point for the Product Service."""
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)