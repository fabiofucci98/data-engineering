"""Shared pytest configuration.

Unit tests run everywhere; integration tests (real Postgres) run only when
RUN_INTEGRATION=1 is set (the GitHub Actions 'city-integration' job).
"""
import os

import pytest


def pytest_collection_modifyitems(config, items) -> None:
    if os.getenv("RUN_INTEGRATION") == "1":
        return
    skip = pytest.mark.skip(
        reason="integration tests need RUN_INTEGRATION=1 + a running Postgres"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)