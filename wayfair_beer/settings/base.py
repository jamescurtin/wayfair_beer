"""Base configuration for the Flask app. It should not be used directly."""
import os


def create_db_uri():
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    db_uri = f"postgresql+psycopg2://{user}:{password}@database:5432/{db}"
    return db_uri


class BaseConfig(object):
    """Configuration common to all environments."""

    SQLALCHEMY_DATABASE_URI = create_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
