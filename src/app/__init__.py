"""
This module initializes the Flask application and loads the necessary configurations.
"""
import logging
import os

from dotenv import load_dotenv
from flask import Flask


def create_app():
    """
    Create and configure the Flask application.

    This function initializes the Flask application, loads environment variables,
    sets up logging, loads configuration from a file or environment variables,
    sets the secret key for CSRF protection, and registers the business locator blueprint.

    Returns:
        Flask: The configured Flask application instance.
    """
    load_dotenv()
    app = Flask(__name__)
    logging.basicConfig(level=logging.DEBUG)

    # Load configuration from a config file or environment variables
    app.config.from_pyfile('config.py', silent=True)

    # Set the secret key for CSRF protection
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

    from .blueprints.business_locator import business_locator
    app.register_blueprint(business_locator)

    return app
