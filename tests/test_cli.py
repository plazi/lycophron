#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Test Lycophron CLI commands."""

import csv
import os
import sqlite3
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
                    "doi",
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
                    "",
                ]
            )

        # Test load command
        result = runner.invoke(lycophron, ["load", "--file", csv_path])

        assert result.exit_code == 0
        assert "Loading finished" in result.output


def test_load_db_objects():
    """Test that the load command correctly commits objects to the database."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Initialize project
        runner.invoke(lycophron, ["init"])

        # Create test file
        files_dir = Path(tmpdir) / "files"
        test_file = files_dir / "test_file.txt"
        with open(test_file, "w") as f:
            f.write("Test content")

        # Create a CSV file with a complete set of required fields
        csv_path = os.path.join(tmpdir, "test_data.csv")
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            # Use new-template as reference for required fields
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
                    "contributors.type",
                    "contributors.given_name",
                    "contributors.family_name",
                    "description",
                    "rights.id",
                    "communities",
                    "doi",
                ]
            )
            writer.writerow(
                [
                    "record1",
                    "Test Record",
                    "2023-01-01",
                    "test_file.txt",
                    "image",
                    "personal",
                    "John",
                    "Doe",
                    "personal",
                    "Jane",
                    "Smith",
                    "This is a test description",
                    "cc-by",
                    "test-community",
                    "",
                ]
            )

        # Run load command
        runner.invoke(lycophron, ["load", "--file", csv_path])

        # Connect to the database directly to verify the objects
        conn = sqlite3.connect(os.path.join(tmpdir, "lycophron.db"))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check Record object
        cursor.execute("SELECT * FROM record WHERE id = ?", ("record1",))
        record = cursor.fetchone()
        assert record is not None
        assert record["id"] == "record1"

        # Verify input_metadata
        metadata = eval(record["input_metadata"])
        assert metadata["metadata"]["title"] == "Test Record"
        assert metadata["metadata"]["publication_date"] == "2023-01-01"
        assert metadata["metadata"]["resource_type"]["id"] == "image"
        assert len(metadata["metadata"]["creators"]) == 1
        assert (
            metadata["metadata"]["creators"][0]["person_or_org"]["type"] == "personal"
        )
        assert (
            metadata["metadata"]["creators"][0]["person_or_org"]["given_name"] == "John"
        )
        assert (
            metadata["metadata"]["creators"][0]["person_or_org"]["family_name"] == "Doe"
        )

        # Check status
        assert record["status"] == "TODO"

        # Check File object
        cursor.execute("SELECT * FROM file WHERE record_id = ?", ("record1",))
        file = cursor.fetchone()
        assert file is not None
        assert file["filename"] == "test_file.txt"
        assert file["status"] == "TODO"  # FileStatus.TODO.value
        assert "md5:" in file["checksum"]

        # Check Community object
        cursor.execute("SELECT * FROM community WHERE record_id = ?", ("record1",))
        community = cursor.fetchone()
        assert community is not None
        assert community["slug"] == "test-community"
        assert community["status"] == "TODO"  # CommunityStatus.TODO.value

        conn.close()


def test_load_multiple_records():
    """Test loading multiple records into the database."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Initialize project
        runner.invoke(lycophron, ["init"])

        # Create CSV file with multiple records
        csv_path = os.path.join(tmpdir, "test_multi.csv")
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
                    "contributors.type",
                    "contributors.given_name",
                    "contributors.family_name",
                    "description",
                    "rights.id",
                    "doi",
                ]
            )
            # Record 1
            writer.writerow(
                [
                    "record1",
                    "First Record",
                    "2023-01-01",
                    "",
                    "image",
                    "personal",
                    "John",
                    "Doe",
                    "personal",
                    "Jane",
                    "Smith",
                    "First record description",
                    "cc-by",
                    "",
                ]
            )
            # Record 2
            writer.writerow(
                [
                    "record2",
                    "Second Record",
                    "2023-02-01",
                    "",
                    "publication",
                    "personal",
                    "Jane",
                    "Smith",
                    "personal",
                    "John",
                    "Doe",
                    "Second record description",
                    "cc-by",
                    "",
                ]
            )

        # Run load command
        runner.invoke(lycophron, ["load", "--file", csv_path])

        # Connect to the database
        conn = sqlite3.connect(os.path.join(tmpdir, "lycophron.db"))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check both records were added
        cursor.execute("SELECT COUNT(*) FROM record")
        count = cursor.fetchone()[0]
        assert count == 2

        # Verify first record metadata
        cursor.execute("SELECT * FROM record WHERE id = ?", ("record1",))
        record1 = cursor.fetchone()
        metadata1 = eval(record1["input_metadata"])
        assert metadata1["metadata"]["title"] == "First Record"

        # Verify second record metadata
        cursor.execute("SELECT * FROM record WHERE id = ?", ("record2",))
        record2 = cursor.fetchone()
        metadata2 = eval(record2["input_metadata"])
        assert metadata2["metadata"]["title"] == "Second Record"
        assert metadata2["metadata"]["resource_type"]["id"] == "publication"
        assert (
            metadata2["metadata"]["creators"][0]["person_or_org"]["family_name"]
            == "Smith"
        )

        conn.close()


def test_load_update_record():
    """Test that loading updates existing records correctly."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Initialize project
        runner.invoke(lycophron, ["init"])

        # Create initial CSV file
        csv_path = os.path.join(tmpdir, "initial.csv")
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
                    "contributors.type",
                    "contributors.given_name",
                    "contributors.family_name",
                    "description",
                    "rights.id",
                    "doi",
                ]
            )
            writer.writerow(
                [
                    "record1",
                    "Original Title",
                    "2023-01-01",
                    "",
                    "image",
                    "personal",
                    "John",
                    "Doe",
                    "personal",
                    "Jane",
                    "Smith",
                    "Original description",
                    "cc-by",
                    "",
                ]
            )

        # Load initial data
        runner.invoke(lycophron, ["load", "--file", csv_path])

        # Create update CSV file
        update_csv_path = os.path.join(tmpdir, "update.csv")
        with open(update_csv_path, "w", newline="") as csvfile:
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
                    "contributors.type",
                    "contributors.given_name",
                    "contributors.family_name",
                    "description",
                    "rights.id",
                    "doi",
                ]
            )
            writer.writerow(
                [
                    "record1",
                    "Updated Title",
                    "2023-02-15",
                    "",
                    "publication",
                    "personal",
                    "Jane",
                    "Smith",
                    "personal",
                    "John",
                    "Doe",
                    "Updated description",
                    "cc-by",
                    "",
                ]
            )

        # Load updated data
        runner.invoke(lycophron, ["load", "--file", update_csv_path])

        # Verify the record was updated
        conn = sqlite3.connect(os.path.join(tmpdir, "lycophron.db"))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM record")
        count = cursor.fetchone()[0]
        assert count == 1, "There should still be only one record"

        cursor.execute("SELECT * FROM record WHERE id = ?", ("record1",))
        record = cursor.fetchone()
        metadata = eval(record["input_metadata"])

        # Check updated fields
        assert metadata["metadata"]["title"] == "Updated Title"
        assert metadata["metadata"]["publication_date"] == "2023-02-15"
        assert metadata["metadata"]["resource_type"]["id"] == "publication"
        assert (
            metadata["metadata"]["creators"][0]["person_or_org"]["given_name"] == "Jane"
        )
        assert (
            metadata["metadata"]["creators"][0]["person_or_org"]["family_name"]
            == "Smith"
        )

        # Check status was reset to TODO
        assert record["status"] == "TODO"

        conn.close()
