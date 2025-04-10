#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Template handling module for Lycophron."""

from typing import Any, Protocol, Self

from .logger import logger


class LazyReference:
    """A lazy reference to a field in another record."""

    def __init__(self, record_id: str, field: str, bidirectional: bool = True):
        """Initialize a lazy reference."""
        self.record_id = record_id
        self.field = field
        self.bidirectional = bidirectional

    def __str__(self) -> str:
        """String representation of the reference."""
        return f"LazyRef({self.record_id}, {self.field}, {self.bidirectional})"

    def with_field(self, new_field: str) -> Self:
        """Return a new reference with an updated field."""
        return LazyReference(self.record_id, new_field, self.bidirectional)


class ReferenceResolver[T](Protocol):
    """Protocol for reference resolvers."""

    def __call__(self, reference: LazyReference) -> T:
        """Resolve a reference to its actual value."""
        ...


class TemplateEngine:
    """Template engine that supports resolving references between records."""

    def __init__(self):
        """Initialize the template engine."""
        pass

    def ref(
        self, record_id: str, field: str, bidirectional: bool = True
    ) -> LazyReference:
        """Create a lazy reference to another record's field."""
        return LazyReference(record_id, field, bidirectional)

    def resolve_reference(
        self, reference: LazyReference, resolver_fn: ReferenceResolver
    ) -> Any:
        """Resolve a reference using the provided resolver function."""
        try:
            return resolver_fn(reference)
        except Exception as e:
            logger.warning(
                "Error resolving reference %s.%s: %s",
                reference.record_id,
                reference.field,
                e,
            )
            return f"Reference error: {reference.record_id}.{reference.field}"
