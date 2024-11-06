import os

from dotenv import load_dotenv
from flask import Flask
import logging


def create_app():
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