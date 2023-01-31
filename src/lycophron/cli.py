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


@click.group()
@click.version_option()
def lycophron():
    """Initialize a cli group."""


@lycophron.command()
@click.argument("keyword")
def init(keyword):
    """Command to intialize the project"""

    # TODO maybe not
    project = Project(keyword)
    project.initialize()


@lycophron.command()
@click.option("--inputfile", required=True)
def validate(inputfile):
    """Command to validate data"""

    # TODO maybe not
    data = Data(inputfile)
    data.validate()


@lycophron.command()
@click.option("--inputfile", required=True)
@click.option("--update", required=False)
def load(inputfile):
    """Loads/Updates CSV into the local DB"""
    # TODO
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
