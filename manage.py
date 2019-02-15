import os

import click

from wayfair_beer.app import create_app
from wayfair_beer.app import run_app
from wayfair_beer.commands.seed_db import seed_db
from wayfair_beer.models import db


@click.group()
def cli():
    """This is a management script for Wayfair Beer App"""


@cli.command()
def run():
    run_app()


@cli.command()
def seed_data():
    create_app()
    seed_db()


if __name__ == "__main__":
    cli()
