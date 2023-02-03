import csv
import os

from .errors import (
    DatabaseAlreadyExists,
    ErrorHandler,
    InvalidRecordData,
)
from .loaders import LoaderFactory
from .schemas.record import RecordRow


class Project:
    def __init__(self, project_folder=os.getcwd()):
        self.project_folder = project_folder
        self.errors = []

    def _load_csv(self, filename):
        with open(filename) as csvfile:
            yield from csv.DictReader(csvfile, delimiter=",", quotechar='"')

    def _validate_record(self, record) -> bool:
        # TODO implement
        if not record["doi"]:
            raise InvalidRecordData(f"Record {record['id']} is invalid: doi not found.")

        return True

    def load_file(self, filename):
        data = self.process_file(filename)
        for record in data:
            self.add_record(record)
        if len(self.errors):
            ErrorHandler.handle_error(self.errors)

    def process_file(self, filename):
        print("Loading file!")
        if not self.is_project_initialized():
            raise Exception("Project is not initialised.")
        # file_path = os.path.join(self.project_folder, filename)
        # factory = LoaderFactory()
        # loader = factory.create_loader(filename)
        # loaded_data = loader.load(file_path)
        row_schema = RecordRow()
        records = []
        for data in self._load_csv(filename):
            try:
                record = row_schema.load(data)
            except Exception as e:
                self.errors.append(e)
            else:
                records.append(record)
        return records

    def add_record(self, record):
        # TODO fix too many "from .db import db"
        from .db import db

        try:
            self._validate_record(record)
            db.add_record(record)
        except Exception as e:
            self.errors.append(e)

    def initialize(self):
        """Initialize the project"""
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
