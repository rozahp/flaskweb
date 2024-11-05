"""Flask configuration."""

import os
import logging

# FLASK CONFIG
class Config:
    """Base config."""
    SECRET_KEY = os.urandom(32)

class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    LOGGING_LEVEL = logging.INFO

class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    LOGGING_LEVEL = logging.DEBUG

