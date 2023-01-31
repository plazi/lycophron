import csv
import os

import click

from lycophron import models


class Project:
    def __init__(self, name):
        self.name = name
        self.current_dir = os.getcwd()
        self.project_dir = self.current_dir + "/" + self.name
        self.files_dir = self.project_dir + "/" + "files"
        self.db_dir = self.project_dir + "/app.db"
        self.csv_dir = self.project_dir + "/input.csv"

    def create_db(self):
        """Create a database"""
        models.create_all()
        click.secho("DB Created!", fg="green")

    def create_csv(self):
        """Create a CSV"""
        header = [
            "id",
            "doi",
            "deposit_id",
            "title",
            "description",
            "creators.name",
            "creators.affiliation",
            "creators.orcid",
            "dwc:kingdom",
            "dwc:order",
            "dwc:family",
            "dwc:collectionCode",
            "related_identifiers.identifier",
            "related_identifiers.relation",
            "files",
        ]

        with open(self.csv_dir, "w", encoding="UTF8") as f:
            writer = csv.writer(f)

            writer.writerow(header)

        click.secho("CSV Created!", fg="green")

    def create_folder(self, create_files_dir="False"):
        """Create a folder"""
        try:
            if create_files_dir == True:
                os.mkdir(self.files_dir)
            else:
                os.mkdir(self.name)

            click.secho("Folder Created!", fg="green")
        except FileExistsError:
            click.secho("The folder already exists!", fg="green")

    def initialize(self):
        """Initialize the project"""
        self.create_folder()
        self.create_folder(True)
        self.create_csv()
        self.create_db()
