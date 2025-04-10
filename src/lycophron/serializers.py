#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron data serializers."""

import csv
import json
from abc import ABC, abstractmethod
from io import StringIO

from .format import Format


class LazyReferenceJSONEncoder(json.JSONEncoder):
    """JSON encoder that can handle LazyReference objects."""

    def default(self, obj):
        from .template import LazyReference

        if isinstance(obj, LazyReference):
            return {
                "type": "lazy_reference",
                "record_id": obj.record_id,
                "field": obj.field,
                "bidirectional": obj.bidirectional,
            }
        return super().default(obj)


class SerializerFactory:
    def create_serializer(self, format):
        return self._get_serializer(format)

    @abstractmethod
    def serialize(self, data, format):
        pass

    def _get_serializer(self, format):
        if format == Format.CSV:
            return CSVSerializer()
        elif format == Format.JSON:
            return JSONSerializer()
        else:
            raise NotImplementedError(
                f"Format {format} is not supported yet! Supported formats: "
                f"{[e.value for e in Format]}"
            )


class Serializer(ABC):
    @abstractmethod
    def serialize(self, data: list, **kwargs) -> str:
        pass


class CSVSerializer(Serializer):
    extension_type = Format.CSV

    def serialize(self, data: list, **kwargs) -> str:
        if not data:
            return ""

        # Process data to handle LazyReference objects
        processed_data = []
        for item in data:
            processed_item = {}
            for key, value in item.items():
                # Convert LazyReference to a string representation if needed
                from .template import LazyReference

                if isinstance(value, LazyReference):
                    processed_value = f"Ref({value.record_id}, {value.field})"
                    processed_item[key] = processed_value
                else:
                    processed_item[key] = value
            processed_data.append(processed_item)

        headers = processed_data[0].keys()
        # Create a string buffer to hold the CSV data
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)

        # Write the header (keys of the dictionary)
        writer.writeheader()

        # Write the data (values of the dictionary)
        writer.writerows(processed_data)

        # Get the CSV content from the buffer
        csv_content = output.getvalue()
        output.close()

        return csv_content


class JSONSerializer(Serializer):
    extension_type = Format.JSON

    def __init__(self) -> None:
        super().__init__()

    def serialize(self, data: list, **kwargs) -> str:
        """Serialize data to JSON format with custom LazyReference encoder."""
        return json.dumps(data, indent=4, cls=LazyReferenceJSONEncoder)
