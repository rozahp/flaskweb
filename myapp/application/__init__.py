from flask import Flask
import os
import atexit
import logging

def init_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.DevConfig')

    # logger
    logging.basicConfig(level=app.config["LOGGING_LEVEL"])

    with app.app_context():

        # Include our Routes
        from . import routes

        return app
