from abc import ABC, abstractmethod
import csv
import os

from .serializers import SerializerFactory
from .format import Format


class Loader(ABC):
    @abstractmethod
    def load(self):
        pass


class LoaderFactory:
    def create_loader(self, filename):
        format = format_from_filename(filename)
        return self._get_loader(format)

    def _get_loader(self, format):
        if format not in [e.value for e in Format]:
            raise NotImplementedError(
                f"Format {format} is not supported yet! Supported formats: {[e.value for e in Format]}"
            )

        if format == Format.CSV.value:
            return CSVLoader()
        else:
            raise ValueError(f"Format not recognized {format}")


class CSVLoader(Loader):

    extension_type = Format.CSV
    fieldnames = []

    def __init__(self) -> None:
        print("Loader init")
        self.serializer = SerializerFactory().create_serializer(self.extension_type)

    def load(self, file_path, batch_size=20):
        print("LOAD")
        format = format_from_filename(file_path)
        if format != self.extension_type.value:
            raise TypeError("CSV Loader only loads .csv files.")

        if batch_size <= 0:
            raise ValueError("Batch size must be a positive integer.")

        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
            count = 0
            data = []
            for row in reader:
                count += 1
                data.append(row)
                if (count % batch_size == 0):
                    yield data
                    data = []
            if (count % batch_size) != 0:
                yield data

def format_from_filename(filename):
    filename, format = os.path.splitext(filename)
    format = format.strip(".")
    return format
