#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Test Lycophron CLI commands."""

import csv
import os
import tempfile
from pathlib import Path

from click.testing import CliRunner

from lycophron.cli import lycophron


def test_init_command_with_name():
    """Test the init command with a project name."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        result = runner.invoke(lycophron, ["init", "testproject"])

        assert result.exit_code == 0
        assert "Project initialized in directory" in result.output

        # Verify project structure
        project_dir = Path(tmpdir) / "testproject"
        assert project_dir.exists()
        assert (project_dir / "files").exists()
        assert (project_dir / "lycophron.cfg").exists()
        assert (project_dir / "lycophron.db").exists()


def test_init_command_default_directory():
    """Test the init command without a project name (uses current directory)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        # Skip the token prompt by providing an empty token
        result = runner.invoke(lycophron, ["init", "--token", ""])

        assert result.exit_code == 0
        assert "Project initialized in directory" in result.output

        # Verify project structure
        assert (Path(tmpdir) / "files").exists()
        assert (Path(tmpdir) / "lycophron.cfg").exists()
        assert (Path(tmpdir) / "lycophron.db").exists()


def test_init_command_with_token():
    """Test the init command with a Zenodo token."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        result = runner.invoke(lycophron, ["init", "--token", "test_token123"])

        assert result.exit_code == 0
        assert "Project initialized in directory" in result.output

        # Verify token in config
        config_path = Path(tmpdir) / "lycophron.cfg"
        assert config_path.exists(), f"Config file not found at {config_path}"

        with open(config_path) as f:
            config_content = f.read()
            assert "TOKEN = 'test_token123'" in config_content


def test_new_template_default():
    """Test the new-template command with default options."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Initialize project first
        runner.invoke(lycophron, ["init"])

        # Generate template
        result = runner.invoke(lycophron, ["new-template"])
        assert result.exit_code == 0

        # Check that template file was created
        template_path = Path(tmpdir) / "data.csv"
        assert template_path.exists()

        # Verify template contains expected columns
        with open(template_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            # Check for required fields
            assert "id" in headers
            assert "filenames" in headers
            assert "title" in headers
            assert "publication_date" in headers


def test_new_template_with_options():
    """Test the new-template command with various options."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Initialize project first
        runner.invoke(lycophron, ["init"])

        # Generate template with options
        custom_path = os.path.join(tmpdir, "custom_template.csv")
        result = runner.invoke(
            lycophron,
            ["new-template", "--file", custom_path, "--custom", "dwc,ac", "--access"],
        )
        assert result.exit_code == 0

        # Check that template file was created
        template_path = Path(custom_path)
        assert template_path.exists()

        # Verify template contains expected columns
        with open(template_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)

            # Check for standard fields
            assert "id" in headers
            assert "filenames" in headers
            assert "title" in headers

            # Check for access fields
            assert "access.files" in headers

            # Check for custom fields
            dwc_fields = [h for h in headers if h.startswith("dwc:")]
            ac_fields = [h for h in headers if h.startswith("ac:")]
            assert len(dwc_fields) > 0
            assert len(ac_fields) > 0


def test_new_template_minimal():
    """Test the new-template command with minimal option."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Initialize project first
        runner.invoke(lycophron, ["init"])

        # Generate minimal template
        result = runner.invoke(lycophron, ["new-template", "--minimal"])
        assert result.exit_code == 0

        # Verify template contains only required fields
        template_path = Path(tmpdir) / "data.csv"
        with open(template_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)

            # Check minimal required fields
            assert "id" in headers
            assert "filenames" in headers
            assert "title" in headers
            assert "publication_date" in headers
            assert "resource_type.id" in headers

            # Should not contain optional fields
            assert not any(h.startswith("dwc:") for h in headers)
            assert not any(h.startswith("ac:") for h in headers)
            assert "access.files" not in headers


def test_load_command():
    """Test the load command with a valid CSV file."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Initialize project
        runner.invoke(lycophron, ["init"])

        # Create a simple CSV file with required fields
        csv_path = os.path.join(tmpdir, "test_data.csv")
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "id",
                    "title",
                    "publication_date",
                    "filenames",
                    "resource_type.id",
                    "creators.type",
                    "creators.given_name",
                    "creators.family_name",
                ]
            )
            writer.writerow(
                [
                    "record1",
                    "Test Record",
                    "2023-01-01",
                    "",
                    "image",
                    "personal",
                    "John",
                    "Doe",
                ]
            )

        # Test load command
        result = runner.invoke(lycophron, ["load", "--file", csv_path])

        assert result.exit_code == 0
        assert "Loading finished" in result.output
