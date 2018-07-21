from wayfair_beer.app import db
from wayfair_beer.app import Beer
from wayfair_beer.app import Brewery
from wayfair_beer.app import KegLocation
from wayfair_beer.app import Office
from wayfair_beer.app import OnTap
from wayfair_beer.app import Rating
from wayfair_beer.app import Tap
from wayfair_beer.app import db


def add_offices():
    copley = Office(
        office_code='MA_Boston_4', office_name='Boston-Copley Place')
    db.session.add(copley)
    db.session.commit()


def add_keglocations():
    third = KegLocation(office_id=1, location_name='Third Floor Kitchen')
    fifth = KegLocation(office_id=1, location_name='Fifth Floor Kitchen')
    seventh_main = KegLocation(
        office_id=1, location_name='Seventh Floor Kitchen Main Keg')
    seventh_cider = KegLocation(
        office_id=1, location_name='Seventh Floor Kitchen Cider Keg')
    db.session.add(third)
    db.session.add(fifth)
    db.session.add(seventh_main)
    db.session.add(seventh_cider)
    db.session.commit()


def add_taps():
    all_taps = {
        1: [
            (1, 'Far Left'),
            (2, 'Middle Left'),
            (3, 'Middle Right'),
            (4, 'Far Right'),
        ],
        2: [
            (1, 'Far Left'),
            (2, 'Middle Left'),
            (3, 'Middle Right'),
            (4, 'Far Right'),
        ],
        3: [
            (1, 'Left'),
            (2, 'Center'),
            (3, 'Right'),
        ],
        4: [
            (1, 'Left'),
            (2, 'Right'),
        ],
    }
    for keglocation, taps in all_taps.items():
        for tap in taps:
            tap_obj = Tap(
                keglocation_id=keglocation, tap_number=tap[0], tap_name=tap[1])
            db.session.add(tap_obj)
    db.session.commit()


def add_breweries():
    unknown = Brewery(
        untappd_brewery_id=-999,
        name='Unknown Brewery',
        image='mystery_beer.jpg',
        untappd_rating=0,
        brewery_type='Unknown',
        city='Boston',
        state='MA',
        country='US')
    db.session.add(unknown)
    db.session.commit()


def add_beers():
    mystery_beer = Beer(
        untappd_beer_id=-999,
        brewery_id=1,
        name='Mystery Beer',
        image='mystery_beer.jpg')

    db.session.add(mystery_beer)
    db.session.commit()


def add_tapped_beers():
    for tap in range(1,14):
        tapped_beer = OnTap(beer_id=1, tap_id=tap)
        db.session.add(tapped_beer)

    db.session.commit()


def seed_db():
    add_offices()
    add_keglocations()
    add_taps()
    add_breweries()
    add_beers()
    add_tapped_beers()
