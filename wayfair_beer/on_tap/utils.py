import os
from os.path import dirname
from urllib.parse import urlparse
from wayfair_beer.models import db
from wayfair_beer.models import Brewery
from wayfair_beer.models import Beer

import requests

from wayfair_beer.api import API

CLIENT_ID = os.environ.get("UNTAPPD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("UNTAPPD_CLIENT_SECRET")


def save_image(app, url, filename, subdirectory=""):
    """Download an image from the internet"""
    r = requests.get(url)
    url_basename = os.path.basename(urlparse(url).path)
    raw_filename, extension = os.path.splitext(url_basename)
    path = os.path.abspath(
        os.path.join(dirname(dirname(__file__)), "static/img", subdirectory)
    )

    with app.open_instance_resource(f"{path}/{filename}{extension}", "wb") as f:
        f.write(r.content)
    return f"{filename}{extension}"


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


def search_beers(app, beer, brewery, limit=5):
    """Search Untappd beer database by beer and brewery name

    Stores beers and breweries that match the search terms to the database
    """
    untappd_url = "https://api.untappd.com/v4"
    api = API(untappd_url)

    query_string = f"{brewery} {beer}".strip()
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "q": query_string,
        "limit": limit,
    }

    response = api.get("search/beer", params=params)
    print(response)
    beer_items = response.get("response", {}).get("beers", {}).get("items", [])
    beers = []
    for beer_item in beer_items:
        beer_data = beer_item["beer"]
        brewery_data = beer_item["brewery"]
        brewery_dict = {"untappd_brewery_id": brewery_data["brewery_id"]}
        brewery_dict_defaults = {
            "name": brewery_data["brewery_name"],
            "image": save_image(
                app,
                brewery_data["brewery_label"],
                f'brewery_{brewery_data["brewery_id"]}',
                subdirectory="labels",
            ),
            "city": brewery_data["location"]["brewery_city"],
            "state": brewery_data["location"]["brewery_state"],
            "lat": brewery_data["location"]["lat"],
            "lng": brewery_data["location"]["lng"],
        }
        brewery, brewery_new = get_or_create(
            db.session, Brewery, defaults=brewery_dict_defaults, **brewery_dict
        )
        if brewery_new:
            brewery_params = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "compact": "true",
            }
            brewery_response = api.get(
                f"brewery/info/{brewery.untappd_brewery_id}", params=brewery_params
            )["response"]
            brewery.country = brewery_response["brewery"]["country_name"]
            brewery.brewery_type = brewery_response["brewery"]["brewery_type"]
            brewery.untappd_rating = brewery_response["brewery"]["rating"][
                "rating_score"
            ]
            db.session.commit()

        beer_dict = {"untappd_beer_id": beer_data["bid"]}
        beer_dict_defaults = {
            "brewery_id": brewery.id,
            "name": beer_data["beer_name"],
            "image": save_image(
                app,
                beer_data["beer_label"],
                f'beer_{beer_data["bid"]}',
                subdirectory="labels",
            ),
            "abv": beer_data["beer_abv"],
            "ibu": beer_data["beer_ibu"],
            "description": beer_data["beer_description"],
            "style": beer_data["beer_style"],
        }
        beer, beer_new = get_or_create(
            db.session, Beer, defaults=beer_dict_defaults, **beer_dict
        )
        if beer_new:
            beer_params = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "compact": "true",
            }
            beer_response = api.get(
                f"beer/info/{beer.untappd_beer_id}", params=beer_params
            )["response"]
            beer.style = beer_response["beer"]["beer_style"]
            beer.untappd_rating = beer_response["beer"]["rating_score"]
            db.session.commit()
        beers.append(beer.id)
    return beers
