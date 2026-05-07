#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Test fixtures for Lycophron."""

import pytest

from lycophron.cli import lycophron


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


def init(runner, token="", project_name=None):
    # Skip the token prompt by providing an empty string token by default.
    cli_args = ["init", "--token", token]
    if project_name:
        cli_args.append(project_name)
    result = runner.invoke(lycophron, cli_args)

    assert result.exit_code == 0
    assert "Project initialized in directory" in result.output

    return result
