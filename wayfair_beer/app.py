import os
from datetime import datetime

from flask import Flask

from wayfair_beer.models import db
from wayfair_beer.models import ma
from wayfair_beer.on_tap.views import on_tap_blueprint
from wayfair_beer.statistics.views import statistics_blueprint


BLUEPRINTS = [on_tap_blueprint, statistics_blueprint]


def create_app():
    app = Flask(__name__)
    configure_app(app)
    register_blueprints(app, BLUEPRINTS)
    db.init_app(app)
    ma.init_app(app)
    app.app_context().push()
    db.create_all()
    return app


def register_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_app(app):
    if "FLASK_CONFIG" in os.environ:
        app.config.from_object(os.environ["FLASK_CONFIG"])
    else:
        app.config.from_object("wayfair_beer.settings.prod.ProdConfig")


app = create_app()


@app.context_processor
def inject_now():
    return {"now": datetime.utcnow()}


def run_app():
    app.run(host="0.0.0.0", port=5000)
