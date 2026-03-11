"""Shared pytest fixtures for doc-rendering-mcp-server tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _blob_settings(monkeypatch: pytest.MonkeyPatch):
    """Set blob storage env vars for all tests."""
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "stcastdevdocs")
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
    yield
