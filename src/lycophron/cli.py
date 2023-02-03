# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron cli tools."""

import click

from lycophron.data import Data
from lycophron.project import Project
from .app import LycophronApp
from .db import db

@click.group()
@click.version_option()
def lycophron():
    """Initialize a cli group."""


@lycophron.command()
@click.option("--token", prompt="Zenodo token", default="CHANGEME")
@click.option("--force", default=False, is_flag=True)
def init(token, force):
    """Command to intialize the project"""
    app = LycophronApp()

    if app.is_config_persisted("token") and not force:
        click.echo(
            "'token' is already defined in configuration file. Use flag --force to override"
        )
    else:
        app.update_app_config({"token": token}, persist=True)
    
    if not app.is_project_initialized():
        app.init_project()
    else:
        if force:
            confirm = click.confirm("You are about to destroy the database. Do you want to proceed?")
            if confirm:
                app.recreate_project()




@lycophron.command()
@click.option("--inputfile", required=True)
def validate(inputfile):
    """Command to validate data"""

    # TODO maybe not
    data = Data(inputfile)
    data.validate()


@lycophron.command()
@click.option("--inputfile", required=True)
def load(inputfile):
    """Loads CSV into the local DB"""
    app = LycophronApp()
    app.load_file(inputfile)
    pass


@lycophron.command()
@click.option("--outputfile", required=True)
def export(outputfile):
    """Exports all records from the DB to a CSV format"""
    # TODO
    pass


@lycophron.command()
def publish():
    """Publishes all records to Zenodo"""
    # TODO
    pass


@lycophron.command()
def update():
    """Edits and updates records on Zenodo"""
    # TODO
    pass


@lycophron.command()
def configure():
    """Configures the application."""
    pass


lycophron.add_command(init)

if __name__ == "__main__":
    lycophron()
