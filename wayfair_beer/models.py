from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from flask_marshmallow import Marshmallow
from marshmallow import fields


def connect_db():
    convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    metadata = MetaData(naming_convention=convention)
    db = SQLAlchemy(metadata=metadata)
    return db


db = connect_db()
ma = Marshmallow()


class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_code = db.Column(db.String(80), unique=True, nullable=False)
    office_name = db.Column(db.String(120), unique=True, nullable=False)
    KegLocations = db.relationship("KegLocation", backref="office", lazy=True)

    def __repr__(self):
        return f"<Office {self.office_name}>"


class KegLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_id = db.Column(db.Integer, db.ForeignKey(Office.id), nullable=False)
    location_name = db.Column(db.String(80), unique=False, nullable=False)
    taps = db.relationship("Tap", backref="keglocation", lazy=True)

    def __repr__(self):
        return f"<KegLocation {self.location_name}>"


class Tap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keglocation_id = db.Column(
        db.Integer, db.ForeignKey(KegLocation.id), nullable=False
    )
    tap_number = db.Column(db.Integer, unique=False, nullable=False)
    tap_name = db.Column(db.String, unique=False, nullable=True)

    def __repr__(self):
        name = self.tap_name if self.tap_name is not None else self.tap_number
        return f"<Tap {name}>"


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
    beers = db.relationship("Beer", backref="brewery", lazy=True)

    def __repr__(self):
        return f"<Brewery {self.name}>"


class Beer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    untappd_beer_id = db.Column(db.Integer, unique=True, nullable=True)
    brewery_id = db.Column(db.Integer, db.ForeignKey(Brewery.id), nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
    image = db.Column(db.String(120), unique=True, nullable=True)
    abv = db.Column(db.Float, unique=False, nullable=True)
    ibu = db.Column(db.Float, unique=False, nullable=True)
    description = db.Column(db.String(4096), unique=False, nullable=True)
    style = db.Column(db.String(120), unique=False, nullable=True)
    untappd_rating = db.Column(db.Float, unique=False, nullable=True)

    def __repr__(self):
        return f"<Beer {self.name}>"


class OnTap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beer_id = db.Column(db.Integer, db.ForeignKey(Beer.id), nullable=False)
    tap_id = db.Column(db.Integer, db.ForeignKey(Tap.id), nullable=False)
    tapped_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_tapped = db.Column(db.Integer, unique=False, nullable=True, default=0)
    ratings = db.relationship("Rating", backref="ontap", lazy=True)

    def __repr__(self):
        return f"<OnTap {self.id}>"


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ontap_id = db.Column(db.Integer, db.ForeignKey(OnTap.id), nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)


class OfficeSchema(ma.ModelSchema):
    KegLocations = fields.Nested("KegLocationSchema", many=True)

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
    brewery = fields.Nested("BrewerySchema", many=False)

    class Meta:
        model = Beer


class OnTapSchema(ma.ModelSchema):
    class Meta:
        model = OnTap


class RatingSchema(ma.ModelSchema):
    class Meta:
        model = Rating
