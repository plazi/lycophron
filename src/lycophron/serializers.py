#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron data serializers."""

import csv
from abc import ABC, abstractmethod
from io import StringIO

from .format import Format


class SerializerFactory:
    def create_serializer(self, format):
        return self._get_serializer(format)

    @abstractmethod
    def serialize(self, data, format):
        pass

    def _get_serializer(self, format):
        if format == Format.CSV:
            return CSVSerializer()
        else:
            raise NotImplementedError(
                f"Format {format} is not supported yet! Supported formats: "
                f"{[e.value for e in Format]}"
            )


class Serializer(ABC):
    @abstractmethod
    def serialize(self, data: list, **kwargs):
        pass


class CSVSerializer(Serializer):
    extension_type = Format.CSV

    def __init__(self) -> None:
        super().__init__()

    def serialize(self, data: list, sep=",") -> str:
        if not data:
            return ""
        headers = data[0].keys()
        # Create a string buffer to hold the CSV data
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers, delimiter=sep)

        # Write the header (keys of the dictionary)
        writer.writeheader()

        # Write the data (values of the dictionary)
        writer.writerows(data)

        # Get the CSV content from the buffer
        csv_content = output.getvalue()
        output.close()

        return csv_content
