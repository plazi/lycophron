#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Test fixtures for Lycophron."""

import pytest


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the LycophronApp singleton between tests."""
    from lycophron.app import SingletonMeta

    # Store original instances
    original_instances = SingletonMeta._instances.copy()

    # Clear instances for this test
    SingletonMeta._instances = {}

    yield

    # Restore original instances after test
    SingletonMeta._instances = original_instances
