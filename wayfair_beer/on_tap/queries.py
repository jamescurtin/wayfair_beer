from pytz import timezone
from sqlalchemy.sql import text

from wayfair_beer.models import db

WHATS_ON_TAP_SQL = text(
    """SELECT id, beer_id, tap_id, tapped_date, name, image,
                 abv, ibu, description, style, untappd_rating, brewery_name,
                 is_tapped
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
          , ROW_NUMBER() OVER(PARTITION BY t.tap_id ORDER BY t.tapped_date DESC) rn
     FROM on_tap t
     JOIN beer b
          ON b.id = t.beer_id
     JOIN brewery br
          ON b.brewery_id = br.id
   ) t
   WHERE t.rn = 1
   ORDER BY beer_id
   """
)


def whats_on_tap():
    """All beers currently on tap"""
    records = db.engine.execute(WHATS_ON_TAP_SQL).fetchall()
    results = {}
    for record in records:
        result = {}
        for key, value in record.items():
            if key == "tap_id":
                tap_id = value
            else:
                if key == "tapped_date":
                    tz = timezone("US/Eastern")
                    utc = timezone("UTC")
                    tz_aware_dt = utc.localize(value)
                    local_dt = tz_aware_dt.astimezone(tz)
                    result[key] = local_dt
                else:
                    result[key] = value
        results[tap_id] = result
    return results
