import os
from datetime import datetime
from urllib.parse import urlparse

import requests
from sqlalchemy import MetaData
from sqlalchemy.sql import text

from flask import Flask, jsonify, render_template, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from wayfair_beer.api import API

CLIENT_ID = os.environ.get('UNTAPPD_CLIENT_ID')
CLIENT_SECRET = os.environ.get('UNTAPPD_CLIENT_SECRET')


def create_app():
    app = Flask(__name__)
    configure_app(app)
    return app


def configure_app(app):
    if 'FLASK_CONFIG' in os.environ:
        app.config.from_object(os.environ['FLASK_CONFIG'])
    else:
        app.config.from_object('wayfair_beer.settings.prod.ProdConfig')


def run_app():
    app.run(host='0.0.0.0', port=5000)


def create_db_uri():
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    db = os.environ['POSTGRES_DB']
    db_uri = f'postgresql+psycopg2://{user}:{password}@database:5432/{db}'
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
    db = SQLAlchemy(app, metadata=metadata)
    return db


def configure_marshmallow(app):
    return Marshmallow(app)


app = create_app()
db = connect_db(app)
ma = configure_marshmallow(app)


class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_code = db.Column(db.String(80), unique=True, nullable=False)
    office_name = db.Column(db.String(120), unique=True, nullable=False)
    KegLocations = db.relationship('KegLocation', backref='office', lazy=True)

    def __repr__(self):
        return f'<Office {self.office_name}>'


class KegLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_id = db.Column(db.Integer, db.ForeignKey(Office.id), nullable=False)
    location_name = db.Column(db.String(80), unique=False, nullable=False)
    taps = db.relationship('Tap', backref='keglocation', lazy=True)

    def __repr__(self):
        return f'<KegLocation {self.location_name}>'


class Tap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keglocation_id = db.Column(
        db.Integer, db.ForeignKey(KegLocation.id), nullable=False)
    tap_number = db.Column(db.Integer, unique=False, nullable=False)
    tap_name = db.Column(db.String, unique=False, nullable=True)

    def __repr__(self):
        name = self.tap_name if self.tap_name is not None else self.tap_number
        return f'<Tap {name}>'


class Brewery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    untappd_brewery_id = db.Column(db.Integer, unique=True, nullable=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    image = db.Column(db.String(120), unique=True, nullable=True)
    untappd_rating = db.Column(db.Float, unique=False, nullable=True)
    brewery_type = db.Column(db.String(120), unique=False, nullable=True)
    city = db.Column(db.String(120), unique=False, nullable=True)
    state = db.Column(db.String(120), unique=False, nullable=True)
    lat = db.Column(db.Float, unique=False, nullable=True)
    lng = db.Column(db.Float, unique=False, nullable=True)
    country = db.Column(db.String(120), unique=False, nullable=True)
    beers = db.relationship('Beer', backref='brewery', lazy=True)

    def __repr__(self):
        return f'<Brewery {self.name}>'


class Beer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    untappd_beer_id = db.Column(db.Integer, unique=True, nullable=True)
    brewery_id = db.Column(
        db.Integer, db.ForeignKey(Brewery.id), nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
    image = db.Column(db.String(120), unique=True, nullable=True)
    abv = db.Column(db.Float, unique=False, nullable=True)
    ibu = db.Column(db.Float, unique=False, nullable=True)
    description = db.Column(db.String(4096), unique=False, nullable=True)
    style = db.Column(db.String(120), unique=False, nullable=True)
    untappd_rating = db.Column(db.Float, unique=False, nullable=True)

    def __repr__(self):
        return f'<Beer {self.name}>'


class OnTap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beer_id = db.Column(db.Integer, db.ForeignKey(Beer.id), nullable=False)
    tap_id = db.Column(db.Integer, db.ForeignKey(Tap.id), nullable=False)
    tapped_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    is_tapped = db.Column(db.Integer, unique=False, nullable=True, default=0)
    ratings = db.relationship('Rating', backref='ontap', lazy=True)

    def __repr__(self):
        return f'<OnTap {self.id}>'


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ontap_id = db.Column(db.Integer, db.ForeignKey(OnTap.id), nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)


class OfficeSchema(ma.ModelSchema):
    KegLocations = fields.Nested('KegLocationSchema', many=True)

    class Meta:
        model = Office


class KegLocationSchema(ma.ModelSchema):
    class Meta:
        model = KegLocation


class TapSchema(ma.ModelSchema):
    class Meta:
        model = Tap


class BrewerySchema(ma.ModelSchema):
    class Meta:
        model = Brewery


class BeerSchema(ma.ModelSchema):
    brewery = fields.Nested('BrewerySchema', many=False)

    class Meta:
        model = Beer


class OnTapSchema(ma.ModelSchema):
    class Meta:
        model = OnTap


class RatingSchema(ma.ModelSchema):
    class Meta:
        model = Rating


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.context_processor
def inject_offices():
    office_schema = OfficeSchema()
    offices = office_schema.dump(Office.query.all(), many=True).data
    return {'offices': offices}


@app.route("/record_rating", methods=['POST'])
def record_rating():
    """Record a beer rating submitted by someone at a keg"""
    ontap_id = request.form['ontap_id']
    rating = request.form['rating']
    star_rating = Rating(ontap_id=ontap_id, rating=rating)
    db.session.add(star_rating)
    db.session.commit()
    return ('', 204)


@app.route("/get_breweries", methods=['POST'])
def get_breweries():
    """Get names of all breweries stored in the database"""
    brewery_schema = BrewerySchema(only=['name'])
    breweries_query_response = Brewery.query.all()
    breweries = [
        brewery['name'] for brewery in brewery_schema.dump(
            breweries_query_response, many=True).data
    ]
    return jsonify(breweries)


@app.route("/get_beers", methods=['POST'])
def get_beers():
    """Get names of all beers stored in the database"""
    beer_schema = BeerSchema(only=['name'])
    beers_query = Beer.query.all()
    beers = [
        beer['name'] for beer in beer_schema.dump(beers_query, many=True).data
    ]
    return jsonify(beers)


@app.route("/tap_new_beer", methods=['POST'])
def tap_new_beer():
    """Based on user input, return all beers that match the beer the user has
    tapped"""
    beer_schema = BeerSchema()

    beer_ids = search_beers(request.form['beer'], request.form['brewery'])

    beers = Beer.query.filter(Beer.id.in_(beer_ids)).all()

    response_dict = {}
    response_dict['beers'] = beer_schema.dump(beers, many=True).data
    response_dict['tap_id'] = request.form['tap_id']
    return jsonify(response_dict)


@app.route("/confirm_tapped_beer", methods=['POST'])
def confirm_tapped_beer():
    """User confirms the beer that has been tapped and updates the dashboard"""
    tapped_beer = OnTap(
        beer_id=request.form['beer_id'], tap_id=request.form['tap_id'])
    db.session.add(tapped_beer)
    db.session.commit()
    return ("", 204)


@app.route("/update_kicked_beer", methods=['POST'])
def update_kicked_beer():
    """Update the status of a keg based on if it has been kicked"""
    ontap_schema = OnTapSchema()

    beer = OnTap.query.filter_by(id=request.form['ontap_id']).first()
    beer_dict = ontap_schema.dump(beer).data

    beer.is_tapped = 1 if beer_dict['is_tapped'] == 0 else 0
    db.session.commit()
    return ("", 204)


def whats_on_tap():
    """All beers currently on tap"""
    sql = text(
       '''SELECT id, beer_id, tap_id, tapped_date, name, image, abv, ibu
                 , description, style, untappd_rating, brewery_name, is_tapped
   FROM (
   SELECT t.id
          , t.tap_id
          , t.beer_id
          , t.tapped_date
          , t.is_tapped
          , b.name
          , b.image
          , b.abv
          , b.ibu
          , b.description
          , b.style
          , b.untappd_rating
          , br.name brewery_name
          , ROW_NUMBER() OVER(PARTITION BY tap_id ORDER BY tapped_date DESC) rn
     FROM on_tap t
     JOIN beer b
          ON b.id = t.beer_id
     JOIN brewery br
          ON b.brewery_id = br.id
   ) t
   WHERE t.rn = 1
   ORDER BY beer_id
   ''')
    records = db.engine.execute(sql).fetchall()
    results = {}
    for record in records:
        result = {}
        for key, value in record.items():
            if key != 'tap_id':
                result[key] = value
            else:
                tap_id = value
        results[tap_id] = result
    return results


def save_image(url, filename, subdirectory=''):
    """Download an image from the internet"""
    r = requests.get(url)
    url_basename = os.path.basename(urlparse(url).path)
    raw_filename, extension = os.path.splitext(url_basename)
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'static/img', subdirectory))
    with app.open_instance_resource(f'{path}/{filename}{extension}',
                                    'wb') as f:
        f.write(r.content)
    return f'{filename}{extension}'


def get_or_create(session, model, defaults=None, **kwargs):
    """Add an object to the database if it doesn't exist; otherwise obtains
    existing object"""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items())
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        session.commit()
        return instance, True


def search_beers(beer, brewery, limit=5):
    """Search Untappd beer database by beer and brewery name

    Stores beers and breweries that match the search terms to the database
    """
    untappd_url = 'https://api.untappd.com/v4'
    api = API(untappd_url)

    query_string = f'{brewery} {beer}'.strip()
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'q': query_string,
        'limit': limit,
    }

    response = api.get('search/beer', params=params)
    print(response)
    beer_items = response.get('response', {}).get('beers', {}).get('items', [])
    beers = []
    for beer_item in beer_items:
        beer_data = beer_item['beer']
        brewery_data = beer_item['brewery']
        brewery_dict = {
            'untappd_brewery_id': brewery_data['brewery_id'],
        }
        brewery_dict_defaults = {
            'name':
            brewery_data['brewery_name'],
            'image':
            save_image(
                brewery_data['brewery_label'],
                f'brewery_{brewery_data["brewery_id"]}',
                subdirectory='labels'),
            'city':
            brewery_data['location']['brewery_city'],
            'state':
            brewery_data['location']['brewery_state'],
            'lat':
            brewery_data['location']['lat'],
            'lng':
            brewery_data['location']['lng'],
        }
        brewery, brewery_new = get_or_create(
            db.session,
            Brewery,
            defaults=brewery_dict_defaults,
            **brewery_dict)
        if brewery_new:
            brewery_params = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'compact': 'true',
            }
            brewery_response = api.get(
                f'brewery/info/{brewery.untappd_brewery_id}',
                params=brewery_params)['response']
            brewery.country = brewery_response['brewery']['country_name']
            brewery.brewery_type = brewery_response['brewery']['brewery_type']
            brewery.untappd_rating = brewery_response['brewery']['rating'][
                'rating_score']
            db.session.commit()

        beer_dict = {
            'untappd_beer_id': beer_data['bid'],
        }
        beer_dict_defaults = {
            'brewery_id':
            brewery.id,
            'name':
            beer_data['beer_name'],
            'image':
            save_image(
                beer_data['beer_label'],
                f'beer_{beer_data["bid"]}',
                subdirectory='labels'),
            'abv':
            beer_data['beer_abv'],
            'ibu':
            beer_data['beer_ibu'],
            'description':
            beer_data['beer_description'],
            'style':
            beer_data['beer_style'],
        }
        beer, beer_new = get_or_create(
            db.session, Beer, defaults=beer_dict_defaults, **beer_dict)
        if beer_new:
            beer_params = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'compact': 'true',
            }
            beer_response = api.get(
                f'beer/info/{beer.untappd_beer_id}',
                params=beer_params)['response']
            beer.style = beer_response['beer']['beer_style']
            beer.untappd_rating = beer_response['beer']['rating_score']
            db.session.commit()
        beers.append(beer.id)
    return beers


@app.route("/")
@app.route("/index")
def index():
    """Index page, which defaults to a dashboard displaying which beers are
    currently on tap"""
    tap_schema = TapSchema()
    keglocation_schema = KegLocationSchema()

    keglocation_id = request.args.get('keglocation_id', 1)
    keglocation_query_response = KegLocation.query.filter_by(
        id=keglocation_id).first()
    keglocation_dict = keglocation_schema.dump(keglocation_query_response).data

    taps = Tap.query.filter_by(keglocation_id=keglocation_id).all()
    taps_dict = tap_schema.dump(taps, many=True).data

    current_beers_dict = whats_on_tap()

    return render_template(
        'index.html',
        taps=taps_dict,
        current_beers=current_beers_dict,
        keglocation=keglocation_dict)


@app.route("/statistics")
def statistics():
    return render_template('statistics.html')
