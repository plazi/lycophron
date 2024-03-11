# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron cli tools."""

from itertools import chain
import csv

import click

from .app import LycophronApp


def _generate_base_fields(prefix, fields):
    """Generates fields with prefixes."""
    return [f"{prefix}.{field}" for field in fields]


def _generate_additional_fields(prefix, fields):
    """Generates fields with prefixes."""
    return [f"{prefix}:{field}" for field in fields]


@click.group()
@click.version_option()
def lycophron():
    """Initialize a cli group."""


@lycophron.command()
@click.argument("pname", required=False)
@click.password_option(
    "--token",
    prompt="Zenodo token",
    default="",
    confirmation_prompt=False,
    required=False,
)
def init(pname=None, token=None):
    """Command to intialize the project"""
    _name = pname or ""
    app = LycophronApp(name=_name)
    app.init()
    if token:
        app.config.update_config({"token": token}, persist=True)
    click.secho(f"Project initialized in directory {app.root_path}.", fg="green")


@lycophron.command()
@click.option("--file", required=True)
def load(file):
    """Loads CSV into the local DB"""
    app = LycophronApp()
    try:
        app.load_file(file)
        click.echo(click.style("Records loaded correctly.", fg="green"))
    except Exception as e:
        click.echo(click.style(e, fg="red"))


@lycophron.command()
@click.option("--outputfile", required=True)
def export(outputfile):
    """Exports all records from the DB to a CSV format"""
    # TODO
    pass


@lycophron.command()
def start():
    """Publishes records to Zenodo. If specified, only n records are published. Otherwise, publishes all."""
    click.secho("Records queued for publishing.", fg="green")
    from .tasks import app as celery_app

    argv = ["worker", "--pool=threads", "--beat", "--loglevel=info"]
    celery_app.worker_main(argv)


@lycophron.command()
def update():
    """Edits and updates records on Zenodo"""
    # TODO
    pass


@lycophron.group()
def config():
    """Modify the application."""
    pass


@config.command()
def show_config():
    """Show the config."""
    pass


@config.command()
@click.argument("name")
def set_config(name):
    """Set a config value."""
    pass


@lycophron.command()
@click.option(
    "--custom",
    type=str,
    help="Custom field namespaces separated by commas (e.g., dwc,ac,obo)",
)
@click.option("--access", is_flag=True, help="Include all fields")
@click.option(
    "--file",
    type=click.File(mode="w", lazy=True),
    default="data.csv",
    help="Output CSV filename",
)
@click.option("--all", is_flag=True, help="Include all fields")
def new_template(
    custom,
    access,
    file,
    all,
):
    """Creates a new CSV template."""
    # Consolidate all fields
    app = LycophronApp()

    all_base_custom_fields = {
        key: _generate_base_fields(
            app.config["BASE_CUSTOM_FIELD_PREFIXES"][key], fields
        )
        for key, fields in app.config["BASE_CUSTOM_FIELD_DEFINITIONS"].items()
    }

    all_additional_custom_fields = {
        key: _generate_additional_fields(
            app.config["ADDITIONAL_CUSTOM_FIELD_PREFIXES"][key], fields
        )
        for key, fields in app.config["ADDITIONAL_CUSTOM_FIELD_DEFINITIONS"].items()
    }
    all_custom_fields = {**all_base_custom_fields, **all_additional_custom_fields}

    # Initialize the list of fields with base lycophron and RDM fields
    fields = app.config["LYCOPHRON_FIELDS"].copy() + app.config["RDM_FIELDS"].copy()
    # Add conditional fields if enabled to headers
    if all:
        fields.extend(app.config["ACCESS_FIELDS"].copy())
        for namespace in chain(
            app.config["BASE_CUSTOM_FIELD_DEFINITIONS"].keys(),
            app.config["ADDITIONAL_CUSTOM_FIELD_DEFINITIONS"].keys(),
        ):
            fields.extend(all_custom_fields.get(namespace, []))
    else:
        if access:
            fields.extend(app.config["ACCESS_FIELDS"].copy())
        if custom:
            namespaces = custom.split(",")
            for namespace in namespaces:
                fields.extend(all_custom_fields.get(namespace, []))

    # Write the fields to the CSV file
    csv_writer = csv.writer(file)
    csv_writer.writerow(fields)


@lycophron.command()
@click.option("--file", prompt="CSV File", type=click.Path(exists=True))
def validate(file):
    """Validates the config and headers of a CSV file."""
    app = LycophronApp()
    app.validate()
    click.secho("App validation passed.", fg="green")

    # Validates headers
    with open(file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        actual_headers = next(reader)  # Read the first row, which contains headers

    # Generate all possible valid headers
    valid_headers = (
        app.config["LYCOPHRON_FIELDS"].copy()
        + app.config["RDM_FIELDS"].copy()
        + app.config["ACCESS_FIELDS"].copy()
        + [
            field
            for key, value in app.config["BASE_CUSTOM_FIELD_DEFINITIONS"].items()
            for field in _generate_base_fields(
                app.config["BASE_CUSTOM_FIELD_PREFIXES"].get(key), value
            )
        ]
        + [
            field
            for key, value in app.config["ADDITIONAL_CUSTOM_FIELD_DEFINITIONS"].items()
            for field in _generate_additional_fields(
                app.config["ADDITIONAL_CUSTOM_FIELD_PREFIXES"].get(key), value
            )
        ]
    )

    # Check if all headers in the CSV are valid
    invalid_headers = [
        header for header in actual_headers if header not in valid_headers
    ]

    if not invalid_headers:
        click.secho("CSV header validation passed.", fg="green")
    else:
        click.secho("CSV header validation failed. Invalid headers found:", fg="red")
        for header in invalid_headers:
            click.secho(f"- {header}", fg="red")


if __name__ == "__main__":
    lycophron()
