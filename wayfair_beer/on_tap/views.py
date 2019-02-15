from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from wayfair_beer.models import Beer
from wayfair_beer.models import BeerSchema
from wayfair_beer.models import Brewery
from wayfair_beer.models import BrewerySchema
from wayfair_beer.models import KegLocation
from wayfair_beer.models import KegLocationSchema
from wayfair_beer.models import Office
from wayfair_beer.models import OfficeSchema
from wayfair_beer.models import OnTap
from wayfair_beer.models import OnTapSchema
from wayfair_beer.models import Rating
from wayfair_beer.models import RatingSchema
from wayfair_beer.models import Tap
from wayfair_beer.models import TapSchema
from wayfair_beer.on_tap.queries import whats_on_tap
from wayfair_beer.on_tap.utils import search_beers
from wayfair_beer.models import db

on_tap_blueprint = Blueprint("on_tap_blueprint", __name__, url_prefix="/")


@on_tap_blueprint.route("/")
@on_tap_blueprint.route("index")
def index():
    """Index page, which defaults to a dashboard displaying which beers are
    currently on tap"""
    tap_schema = TapSchema()
    keglocation_schema = KegLocationSchema()

    keglocation_id = request.args.get("keglocation_id", 1)
    keglocation_query_response = KegLocation.query.filter_by(id=keglocation_id).first()
    keglocation_dict = keglocation_schema.dump(keglocation_query_response).data

    taps = Tap.query.filter_by(keglocation_id=keglocation_id).all()
    taps_dict = tap_schema.dump(taps, many=True).data

    current_beers_dict = whats_on_tap()

    return render_template(
        "index.html",
        taps=taps_dict,
        current_beers=current_beers_dict,
        keglocation=keglocation_dict,
    )


@on_tap_blueprint.route("record_rating", methods=["POST"])
def record_rating():
    """Record a beer rating submitted by someone at a keg"""
    ontap_id = request.form["ontap_id"]
    rating = request.form["rating"]
    star_rating = Rating(ontap_id=ontap_id, rating=rating)
    db.session.add(star_rating)
    db.session.commit()
    return ("", 204)


@on_tap_blueprint.route("get_breweries", methods=["POST"])
def get_breweries():
    """Get names of all breweries stored in the database"""
    brewery_schema = BrewerySchema(only=["name"])
    breweries_query_response = Brewery.query.all()
    breweries = [
        brewery["name"]
        for brewery in brewery_schema.dump(breweries_query_response, many=True).data
    ]
    return jsonify(breweries)


@on_tap_blueprint.route("get_beers", methods=["POST"])
def get_beers():
    """Get names of all beers stored in the database"""
    beer_schema = BeerSchema(only=["name"])
    beers_query = Beer.query.all()
    beers = [beer["name"] for beer in beer_schema.dump(beers_query, many=True).data]
    return jsonify(beers)


@on_tap_blueprint.route("tap_new_beer", methods=["POST"])
def tap_new_beer():
    """Based on user input, return all beers that match the beer the user has
    tapped"""
    beer_schema = BeerSchema()

    beer_ids = search_beers(current_app, request.form["beer"], request.form["brewery"])

    beers = Beer.query.filter(Beer.id.in_(beer_ids)).all()

    response_dict = {}
    response_dict["beers"] = beer_schema.dump(beers, many=True).data
    response_dict["tap_id"] = request.form["tap_id"]
    return jsonify(response_dict)


@on_tap_blueprint.route("confirm_tapped_beer", methods=["POST"])
def confirm_tapped_beer():
    """User confirms the beer that has been tapped and updates the dashboard"""
    tapped_beer = OnTap(beer_id=request.form["beer_id"], tap_id=request.form["tap_id"])
    db.session.add(tapped_beer)
    db.session.commit()
    return ("", 204)


@on_tap_blueprint.route("update_kicked_beer", methods=["POST"])
def update_kicked_beer():
    """Update the status of a keg based on if it has been kicked"""
    ontap_schema = OnTapSchema()

    beer = OnTap.query.filter_by(id=request.form["ontap_id"]).first()
    beer_dict = ontap_schema.dump(beer).data

    beer.is_tapped = 1 if beer_dict["is_tapped"] == 0 else 0
    db.session.commit()
    return ("", 204)


@on_tap_blueprint.context_processor
def inject_offices():
    office_schema = OfficeSchema()
    offices = office_schema.dump(Office.query.all(), many=True).data
    return {"offices": offices}
