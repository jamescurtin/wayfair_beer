import os

import click
from wayfair_beer.app import Beer
from wayfair_beer.app import Brewery
from wayfair_beer.app import KegLocation
from wayfair_beer.app import Office
from wayfair_beer.app import OnTap
from wayfair_beer.app import Rating
from wayfair_beer.app import Tap
from wayfair_beer.app import app
from wayfair_beer.app import connect_db
from wayfair_beer.app import db
from wayfair_beer.app import run_app
from wayfair_beer.commands.seed_db import seed_db


@click.group()
def cli():
    """This is a management script for Wayfair Beer App"""


@cli.command()
def run():
    run_app()


@cli.command()
def seed_data():
    seed_db()


@cli.command()
def create_schema():
    db.create_all()


if __name__ == '__main__':
    cli()
