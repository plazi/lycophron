#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron cli tools."""

import csv
import signal
import subprocess
import sys
import time
from itertools import chain
from multiprocessing import Process
from pathlib import Path

import click

from .app import LycophronApp
from .logger import logger

INFO_COLOR = "cyan"


def _generate_base_fields(prefix, fields):
    """Generates fields with prefixes."""
    return [f"{prefix}.{field}" for field in fields]


def _generate_additional_fields(prefix, fields):
    """Generates fields with prefixes."""
    return [f"{prefix}:{field}" for field in fields]


@click.group()
@click.version_option()
def lycophron():
    """Lycophron is a tool to batch upload records to Zenodo using a CSV file."""


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
    """Intialize the project."""
    try:
        _name = pname or ""
        app = LycophronApp(name=_name)
        app.init()
        if token:
            app.config.update_config({"token": token}, persist=True)
    except Exception as e:
        click.secho(f"Error initializing project: {e}.", fg="red")
        return

    click.secho(f"Project initialized in directory {app.root_path}.", fg="green")


@lycophron.command()
@click.option("--file", required=True)
def load(file):
    """Load CSV into the local DB."""
    app = LycophronApp()
    logger.debug(f"Loading file {file}")
    try:
        app.load_file(file)
        click.echo(
            click.style(
                "Loading finished. See messages above for results.", fg=INFO_COLOR
            )
        )
    except Exception as e:
        click.echo(click.style(e, fg="red"))
    logger.debug(f"File {file} finished loading.")


@lycophron.command()
@click.option(
    "--file",
    type=click.File(mode="w", lazy=True),
    default="export.csv",
    help="Export CSV filename",
)
@click.option("--all", is_flag=True, help="Include all fields", default=False)
def export(file, all):
    """Export all records from the DB to a CSV format."""
    app = LycophronApp()
    logger.debug("Exporting data.")
    try:
        export = app.project.export(app.config, full=all)
    except NotImplementedError:
        click.echo(
            click.style(
                "Flag --all is not supported yet. Only basic fields will be exported.",
                fg="yellow",
            )
        )
        export = app.project.export(app.config, full=False)
    click.echo(export)
    file.write(export)
    file.close()
    logger.debug("Finished exporting data.")
    click.echo(click.style(f"Exported data to {file.name}.", fg=INFO_COLOR))


@lycophron.command()
def start():
    """Starts the background worker for publishing records."""
    click.secho("Starting Celery worker and beat scheduler...", fg=INFO_COLOR)

    processes = []

    def signal_handler(signum, frame):
        """Handle termination signals."""
        click.secho("\nShutting down Celery processes...", fg="yellow")
        for proc in processes:
            if isinstance(proc, subprocess.Popen):
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            elif isinstance(proc, Process):
                proc.terminate()
                proc.join(timeout=5)
                if proc.is_alive():
                    proc.kill()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if hasattr(signal, "SIGBREAK"):  # Windows
        signal.signal(signal.SIGBREAK, signal_handler)

    try:
        # Start Celery worker process
        worker_cmd = [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "lycophron.tasks",
            "worker",
            "--pool=threads",
            "--loglevel=info",
        ]
        worker_process = subprocess.Popen(worker_cmd)
        processes.append(worker_process)

        # Give worker time to start
        time.sleep(2)

        # Start Celery beat process
        beat_cmd = [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "lycophron.tasks",
            "beat",
            "--loglevel=info",
        ]
        beat_process = subprocess.Popen(beat_cmd)
        processes.append(beat_process)

        click.secho(
            "Celery worker and beat scheduler started successfully.", fg="green"
        )
        click.secho("Press Ctrl+C to stop.", fg=INFO_COLOR)

        # Wait for processes
        while True:
            # Check if processes are still running
            for proc in processes:
                if proc.poll() is not None:
                    click.secho(f"Process exited with code {proc.returncode}", fg="red")
                    signal_handler(None, None)
            time.sleep(1)

    except Exception as e:
        click.secho(f"Error starting Celery: {e}", fg="red")
        signal_handler(None, None)


@lycophron.command()
@click.option("--file", required=True)
@click.pass_context
def update(ctx, file):
    """Update record locally."""
    ctx.forward(load)
    ctx.invoke(load, file=file)


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
@click.option("--access", is_flag=True, help="Include access fields")
@click.option(
    "--file",
    type=click.File(mode="w", lazy=True),
    default="data.csv",
    help="Output CSV filename",
)
@click.option("--all", is_flag=True, help="Include all fields.")
@click.option("--minimal", is_flag=True, default=False, help="Include minimal fields")
def new_template(custom, access, file, all, minimal):
    """Creates a new CSV template.

    By default, the template includes the minimal required fields and a small
    subset of RDM fields.
    """
    # Consolidate all fields
    app = LycophronApp()

    if all and minimal:
        click.secho("Cannot use both --all and --minimal flags.", fg="red")
        return

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
    fields = app.config["LYCOPHRON_FIELDS"].copy()
    # Add conditional fields if enabled to headers
    if all:
        fields.extend(app.config["RDM_FIELDS"].copy())
        fields.extend(app.config["ACCESS_FIELDS"].copy())
        for namespace in chain(
            app.config["BASE_CUSTOM_FIELD_DEFINITIONS"].keys(),
            app.config["ADDITIONAL_CUSTOM_FIELD_DEFINITIONS"].keys(),
        ):
            fields.extend(all_custom_fields.get(namespace, []))
    elif minimal:
        fields.extend(app.config["REQUIRED_FIELDS"].copy())
    else:
        fields.extend(app.config["RDM_FIELDS"].copy())
        if access:
            fields.extend(app.config["ACCESS_FIELDS"].copy())
        if custom:
            namespaces = custom.split(",")
            for namespace in namespaces:
                fields.extend(all_custom_fields.get(namespace, []))

    # Write the fields to the CSV file
    csv_writer = csv.writer(file)
    # Dump fields, removing duplicates
    csv_writer.writerow(list(dict.fromkeys(fields)))


@lycophron.command()
@click.option("--file", prompt="CSV File", type=click.Path(exists=True))
def validate(file):
    """Validate the config and headers of a CSV file."""
    try:
        app = LycophronApp()
        app.validate()
    except Exception as e:
        click.secho(f"App validation failed: {e}", fg="red")
        return
    click.secho("App is valid.", fg="green")

    # Validates headers
    with open(file, newline="", encoding="utf-8") as csvfile:
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

    try:
        app.project.validate(file, app.config, Path(app.root_path) / "files")
    except Exception as e:
        click.secho(f"Data validation failed: {e}", fg="red")
        return
    click.secho("Data and files validation passed.", fg="green")


@lycophron.command()
def retry_failed():
    """Set failed records to be retried."""
    app = LycophronApp()
    queued_records = 0
    try:
        queued_records = app.project.retry_failed()
    except Exception as e:
        click.secho(f"Failed to retry records: {e}", fg="red")
        return
    click.secho(f"{queued_records} records queued for retrying.", fg=INFO_COLOR)


@lycophron.command()
def recreate():
    """Recreate the project."""
    try:
        app = LycophronApp()
        # Are you sure?
        click.confirm(
            (
                "Are you sure you want to recreate the project? "
                "This will delete all records and files."
            ),
            abort=True,
        )
        app.recreate()
        click.secho("Project recreated.", fg=INFO_COLOR)
    except click.Abort:
        click.secho("Recreation aborted.", fg=INFO_COLOR)
    except Exception as e:
        click.secho(f"Error recreating project: {e}", fg="red")


if __name__ == "__main__":
    lycophron()
