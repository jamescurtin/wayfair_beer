import os

import click

from wayfair_beer.commands.seed_db import seed_db
from wayfair_beer.app import db
from wayfair_beer.app import run_app


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
