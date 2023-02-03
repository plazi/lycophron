# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron data loaders."""

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
        self.serializer = SerializerFactory().create_serializer(self.extension_type)

    def load(self, file_path, batch_size=20):
        format = format_from_filename(file_path)
        if format != self.extension_type.value:
            raise TypeError("CSV Loader only loads .csv files.")

        if batch_size <= 0:
            raise ValueError("Batch size must be a positive integer.")

        with open(file_path) as csvfile:
            yield from csv.DictReader(csvfile, delimiter=",", quotechar='"')


def format_from_filename(filename):
    filename, format = os.path.splitext(filename)
    format = format.strip(".")
    return format
