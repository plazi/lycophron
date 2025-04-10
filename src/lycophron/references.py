#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Reference management module for Lycophron."""

from typing import Any

from sqlalchemy.orm import Session

from .models import Record, Reference
from .template import LazyReference, TemplateEngine


class ReferenceManager:
    """Manager for handling references between records."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session
        self.template_engine = TemplateEngine()

    def extract_references(self, record_data: dict) -> list[dict]:
        """Extract references from record data."""
        references = []

        def process_value(value: Any, field_path: str) -> None:
            """Process a value recursively to extract references."""
            if isinstance(value, dict):
                for k, v in value.items():
                    new_path = f"{field_path}.{k}" if field_path else k
                    process_value(v, new_path)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    new_path = f"{field_path}[{i}]" if field_path else f"[{i}]"
                    process_value(item, new_path)
            elif isinstance(value, LazyReference):
                references.append(
                    {
                        "source_field": field_path,
                        "target_record_id": value.record_id,
                        "target_field": value.field,
                        "bidirectional": value.bidirectional,
                    }
                )

        # Process metadata dictionary to extract all templates/references
        metadata = record_data.get("input_metadata", {})
        process_value(metadata, "")

        return references

    def store_references(self, record_id: str, references: list[dict]) -> None:
        """Store references for a record."""
        # Clear existing references for this record
        self.session.query(Reference).filter(
            Reference.source_record_id == record_id
        ).delete()

        # Add new references
        for ref in references:
            reference = Reference(
                source_record_id=record_id,
                target_record_id=ref["target_record_id"],
                source_field=ref["source_field"],
                target_field=ref["target_field"],
                bidirectional=str(ref["bidirectional"]),
            )
            self.session.add(reference)

        self.session.commit()

    def get_record_field_value(self, record_id: str, field_path: str) -> Any:
        """Get a field value from a record by its path."""
        record = self.session.get(Record, record_id)
        if record is None:
            return None

        # Navigate through the nested structure using the field path
        value = record.input_metadata
        parts = field_path.split(".")

        for part in parts:
            # Handle array indexing in field path like 'creators[0].name'
            if "[" in part and "]" in part:
                array_part, idx_part = part.split("[", 1)
                idx = int(idx_part.split("]")[0])
                if array_part:
                    value = value.get(array_part, [])
                try:
                    value = value[idx]
                except (IndexError, TypeError):
                    return None
            else:
                try:
                    value = value.get(part, {})
                except (AttributeError, TypeError):
                    return None

        return value

    def resolve_references(self, record: Record) -> Record:
        """Resolve all lazy references for a record."""
        if not record or not record.input_metadata:
            return record

        # Create a resolver function
        def resolver(reference: LazyReference) -> Any:
            return self.get_record_field_value(reference.record_id, reference.field)

        # Process all fields in the input_metadata
        def process_dict(data: dict) -> dict:
            if not isinstance(data, dict):
                return data

            result = {}
            for key, value in data.items():
                result[key] = process_item(value)
            return result

        def process_item(item: Any) -> Any:
            match item:
                case dict():
                    return process_dict(item)
                case list():
                    return [process_item(i) for i in item]
                case LazyReference():
                    return self.template_engine.resolve_reference(item, resolver)
                case _:
                    return item

        # Create a copy to avoid modifying the original
        resolved_metadata = process_dict(record.input_metadata)

        # Create a new record object with resolved references
        record_data = {"id": record.id, "upload_id": record.upload_id}
        record_data |= {"input_metadata": resolved_metadata}
        record_data |= {"remote_metadata": record.remote_metadata}
        record_data |= {"status": record.status}
        record_data |= {"response": record.response, "error": record.error}
        result_record = Record(**record_data)

        return result_record
