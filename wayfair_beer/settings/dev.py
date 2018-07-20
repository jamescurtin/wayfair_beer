from wayfair_beer.settings.base import BaseConfig


class DevConfig(BaseConfig):
    LOG_LEVEL = 'INFO'
    FLASK_DEBUG = True

