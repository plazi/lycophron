import csv
import os

import click

from .errors import DatabaseAlreadyExists, ErrorHandler
from .loaders import LoaderFactory


class Project:
    def __init__(self, project_folder=os.getcwd()):
        self.project_folder = project_folder

    def load_file(self, filename):
        print("Loading file!")
        return
        file_path = os.path.join(self.project_folder, filename)
        loader = LoaderFactory.create_loader(filename)
        loaded_data = loader.load(file_path)
        deserialized_data = loader.deserializer.deserialize(loaded_data)

    # def create_csv(self):
    #     """Create a CSV"""
    #     header = [
    #         "id",
    #         "doi",
    #         "deposit_id",
    #         "title",
    #         "description",
    #         "creators.name",
    #         "creators.affiliation",
    #         "creators.orcid",
    #         "dwc:kingdom",
    #         "dwc:order",
    #         "dwc:family",
    #         "dwc:collectionCode",
    #         "related_identifiers.identifier",
    #         "related_identifiers.relation",
    #         "files",
    #     ]

    #     with open(self.csv_dir, "w", encoding="UTF8") as f:
    #         writer = csv.writer(f)

    #         writer.writerow(header)

    #     click.secho("CSV Created!", fg="green")

    # def create_folder(self, create_files_dir="False"):
    #     """Create a folder"""
    #     try:
    #         if create_files_dir == True:
    #             os.mkdir(self.files_dir)
    #         else:
    #             os.mkdir(self.name)

    #         click.secho("Folder Created!", fg="green")
    #     except FileExistsError:
    #         click.secho("The folder already exists!", fg="green")

    def initialize(self):
        """Initialize the project"""
        # self.create_folder()
        # self.create_folder(True)
        # self.create_csv()
        from .db import db

        try:
            db.init_db()
        except DatabaseAlreadyExists as e:
            ErrorHandler.handle_error(e)

    def recreate_project(self):
        from .db import db

        db.recreate_db()

    
    def validate_project(self):
        raise NotImplementedError("Project validation not implemented yet")

    
    def is_project_initialized(self):
        from .db import db
        
        return db.database_exists()
