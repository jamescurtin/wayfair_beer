import os

from sqlalchemy import MetaData

from flask import Flask, render_template
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from wayfair_beer.api import API


def create_app():
    app = Flask(__name__)
    configure_app(app)
    return app


def configure_app(app):
    if 'FLASK_CONFIG' in os.environ:
        app.config.from_object(os.environ['FLASK_CONFIG'])
    else:
        app.config.from_object('dashboard.settings.prod.ProdConfig')


def run_app():
    app.run(host='0.0.0.0', port=5000)


def create_db_uri():
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['APP_URL']
    database = os.environ['POSTGRES_DB']
    db_uri = f'postgresql+psycopg2://{user}:{password}@database:5432/{database}'
    return db_uri


def connect_db(app):
    convention = {
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
    metadata = MetaData(naming_convention=convention)
    db_uri = create_db_uri()
    db = SQLAlchemy(app, metadata=metadata)
    return db


def configure_marshmallow(app):
    return Marshmallow(app)


app = create_app()
db = connect_db(app)
ma = configure_marshmallow(app)



@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')
