# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron cli tools."""

import click
import csv

from lycophron.errors import InvalidDirectoryError
from .app import LycophronApp

lycophron_fields = ["id", "filenames"]

# Base RDM fields
rdm_fields = [
    "resource_type.id",
    "creators.type",
    "creators.given_name",
    "creators.family_name",
    "creators.name",
    "creators.orcid",
    "creators.gnd",
    "creators.isni",
    "creators.ror",
    "creators.role.id",
    "creators.affiliations.id",
    "creators.affiliations.name",
    "title",
    "publication_date",
    # "additional_titles.title",
    # "additional_titles.type.id",
    # "additional_titles.lang.id",
    "description",
    "abstract.description",  # This is an additional_descriptions
    # "abstract.lang.id",
    "method.description",  # This is an additional_descriptions
    # "method.lang.id",
    "notes.description",  # This is an additional_descriptions
    # "notes.lang.id",
    # "other.description",  # This is an additional_descriptions
    # "other.lang.id",
    # "series-information.description",  # This is an additional_descriptions
    # "series-information.lang.id",
    # "table-of-contents.description",  # This is an additional_descriptions
    # "table-of-contents.lang.id",
    # "technical-info.description",  # This is an additional_descriptions
    # "technical-info.lang.id",
    "rights.id",
    "rights.title",
    # "rights.description",
    # "rights.link",
    "contributors.type",
    "contributors.given_name",
    "contributors.family_name",
    "contributors.name",
    "contributors.orcid",
    "contributors.gnd",
    "contributors.isni",
    "contributors.ror",
    "contributors.role.id",
    "contributors.affiliations.id",
    "contributors.affiliations.name",
    # "subjects.id",
    "subjects.subject",
    "languages.id",
    # "dates.date",
    # "dates.type.id",
    # "dates.description",
    "version",
    "publisher",
    "identifiers.identifier",
    # "identifiers.scheme",  # Auto guessed
    "related_identifiers.identifier",
    # "related_identifiers.scheme",  # Auto guessed
    "related_identifiers.relation_type.id",
    "related_identifiers.resource_type.id",
    # "funding.funder.id",
    # "funding.funder.name",
    # "funding.award.id",
    # "funding.award.title",
    # "funding.award.number",
    # "funding.award.identifiers.scheme",
    # "funding.award.identifiers.identifier",
    "references.reference",
    # "references.identifier",
    # "references.scheme",
    "default_community",
    "communities",
    "doi",
    "locations.lat",
    "locations.lon",
    "locations.place",
    "locations.description",
]

access_fields = [
    "access.files",
    "access.embargo.active",
    "access.embargo.until",
    "access.embargo.reason",
]

# Field prefixes
field_prefixes = {
    "journal": "journal",
    "meeting": "meeting",
    "imprint": "imprint",
    "thesis": "university",
    "dwc": "dwc",
    "gbif-dwc": "gbif-dwc",
    "ac": "ac",
    "dc": "dc",
    "openbiodiv": "openbiodiv",
    "obo": "obo",
}

# Field definitions
field_definitions = {
    "journal": ["title", "issue", "volume", "pages", "issn"],
    "meeting": [
        "acronym",
        "dates",
        "place",
        "session_part",
        "session",
        "title",
        "url",
    ],
    "imprint": ["title", "isbn", "pages", "place"],
    "thesis": ["thesis"],
    "dwc": [
        "basisOfRecord",
        "catalogNumber",
        "class",
        "collectionCode",
        "country",
        "county",
        "dateIdentified",
        "decimalLatitude",
        "decimalLongitude",
        "eventDate",
        "family",
        "genus",
        "identifiedBy",
        "individualCount",
        "institutionCode",
        "kingdom",
        "lifeStage",
        "locality",
        "materialSampleID",
        "namePublishedInID",
        "namePublishedInYear",
        "order",
        "otherCatalogNumbers",
        "phylum",
        "preparations",
        "recordedBy",
        "scientificName",
        "scientificNameAuthorship",
        "scientificNameID",
        "sex",
        "specificEpithet",
        "stateProvince",
        "taxonID",
        "taxonRank",
        "taxonomicStatus",
        "typeStatus",
        "verbatimElevation",
        "verbatimEventDate",
    ],
    "gbif-dwc": ["identifiedByID", "recordedByID"],
    "ac": [
        "associatedSpecimenReference",
        "captureDevice",
        "physicalSetting",
        "resourceCreationTechnique",
        "subjectOrientation",
        "subjectPart",
    ],
    "dc": ["creator", "rightsHolder"],
    "openbiodiv": ["TaxonomicConceptLabel"],
    "obo": ["RO_0002453"],
}


def _generate_fields(prefix, fields):
    """Generates fields with prefixes."""
    return [f"{prefix}.{field}" for field in fields]


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
            confirm = click.confirm(
                "You are about to destroy the database and wipe the .files/ directory. Do you want to proceed?"
            )
            if confirm:
                app.recreate_project()


@lycophron.command()
@click.option("--inputfile", required=True)
def validate(inputfile):
    """Command to validate data"""

    # TODO maybe not
    app = LycophronApp()


@lycophron.command()
@click.option("--inputfile", required=True)
def load(inputfile):
    """Loads CSV into the local DB"""
    app = LycophronApp()
    app.load_file(inputfile)


@lycophron.command()
@click.option("--outputfile", required=True)
def export(outputfile):
    """Exports all records from the DB to a CSV format"""
    # TODO
    pass


@lycophron.command()
@click.option("-n", "--num_records", default=None)
def publish(num_records):
    """Publishes records to Zenodo. If specified, only n records are published. Otherwise, publishes all."""
    app = LycophronApp()
    app.publish_records(num_records)
    from .tasks import app as celery_app

    argv = ["worker", "--loglevel=info"]
    celery_app.worker_main(argv)


@lycophron.command()
def update():
    """Edits and updates records on Zenodo"""
    # TODO
    pass


@lycophron.command()
def configure():
    """Configures the application."""
    pass


@lycophron.command()
@click.option(
    "--custom",
    type=str,
    help="Custom field namespaces separated by commas (e.g., dwc,ac,obo)",
)
@click.option("--access", is_flag=True, help="Include all fields")
@click.option(
    "--filename",
    type=click.File(mode="w", lazy=True),
    default="data.csv",
    help="Output CSV filename",
)
@click.option("--all", is_flag=True, help="Include all fields")
def new_template(
    custom,
    access,
    filename,
    all,
):
    """Creates a new CSV template."""
    # Consolidate all fields
    all_fields = {
        key: _generate_fields(field_prefixes[key], fields)
        for key, fields in field_definitions.items()
    }

    # Initialize the list of fields with base lycophron and RDM fields
    fields = lycophron_fields.copy() + rdm_fields.copy()
    # Add conditional fields if enabled to headers
    if all:
        fields.extend(access_fields.copy())
        for namespace in field_definitions.keys():
            fields.extend(all_fields.get(namespace, []))
    else:
        if access:
            fields.extend(access_fields.copy())
        if custom:
            namespaces = custom.split(",")
            for namespace in namespaces:
                fields.extend(all_fields.get(namespace, []))

    # Write the fields to the CSV file
    csv_writer = csv.writer(filename)
    csv_writer.writerow(fields)


@lycophron.command()
@click.option("--file", prompt="CSV File", type=click.Path(exists=True))
def validate(file):
    """Validates the config and headers of a CSV file."""
    app = LycophronApp()
    # Validates config
    try:
        app.validate_project()
        click.echo(click.style("Configuration validation passed.", fg="green"))
    except (ValueError, InvalidDirectoryError) as e:
        click.echo(click.style(e, fg="red"))
        return

    # Validates headers
    with open(file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        actual_headers = next(reader)  # Read the first row, which contains headers

    # Generate all possible valid headers
    valid_headers = (
        lycophron_fields.copy()
        + rdm_fields.copy()
        + access_fields.copy()
        + [
            field
            for key, value in field_definitions.items()
            for field in _generate_fields(field_prefixes.get(key), value)
        ]
    )

    # Check if all headers in the CSV are valid
    invalid_headers = [
        header for header in actual_headers if header not in valid_headers
    ]

    if not invalid_headers:
        click.echo(click.style("CSV header validation passed.", fg="green"))
    else:
        click.echo(
            click.style(
                "CSV header validation failed. Invalid headers found:", fg="red"
            )
        )
        for header in invalid_headers:
            click.echo(click.style(f"- {header}", fg="red"))


lycophron.add_command(init)

if __name__ == "__main__":
    lycophron()
