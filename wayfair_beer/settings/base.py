"""Base configuration for the Flask app. It should not be used directly."""
from wayfair_beer.app import create_db_uri


class BaseConfig(object):
    """Configuration common to all environments."""
    SQLALCHEMY_DATABASE_URI = create_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
