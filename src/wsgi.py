"""
WSGI entry point for the application.
"""
from app import create_app

# Create the WSGI application
app = create_app()

if __name__ == "__main__":
    # Run the application
    app.run()
