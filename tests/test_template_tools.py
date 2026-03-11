"""Tests for template registry and validation tools."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from doc_rendering_mcp_server.models import TemplateEntry, TemplateFormat, TemplateRegistry
from doc_rendering_mcp_server.tools.template_tools import (
    get_template_info,
    load_template_registry,
    validate_context,
)


def test_load_template_registry() -> None:
    """Registry loads and parses templates.yaml."""
    load_template_registry.cache_clear()
    registry = load_template_registry()
    assert isinstance(registry, TemplateRegistry)
    assert registry.version == "1.0"
    assert len(registry.templates) >= 4
    load_template_registry.cache_clear()


def test_load_template_registry_has_expected_templates() -> None:
    """Registry contains all expected template keys."""
    load_template_registry.cache_clear()
    registry = load_template_registry()
    expected = {"user_guide", "use_case", "sprint_report", "functional_spec"}
    assert expected.issubset(set(registry.templates.keys()))
    load_template_registry.cache_clear()


def test_get_template_info_valid() -> None:
    """get_template_info returns entry for known template."""
    load_template_registry.cache_clear()
    entry = get_template_info("sprint_report")
    assert entry.display_name == "Sprint Report"
    assert "html" in entry.formats
    assert "sprint_name" in entry.required_fields
    load_template_registry.cache_clear()


def test_get_template_info_invalid() -> None:
    """get_template_info raises KeyError for unknown template."""
    load_template_registry.cache_clear()
    with pytest.raises(KeyError, match="nonexistent"):
        get_template_info("nonexistent")
    load_template_registry.cache_clear()


def test_validate_context_all_present() -> None:
    """Returns empty list when all required fields present."""
    load_template_registry.cache_clear()
    missing = validate_context("sprint_report", {
        "sprint_name": "Sprint 3",
        "team_name": "Alpha",
        "project_name": "Cast",
        "start_date": "2026-03-01",
        "end_date": "2026-03-14",
        "planned_points": 30,
        "completed_points": 25,
        "velocity": 25,
    })
    assert missing == []
    load_template_registry.cache_clear()


def test_validate_context_missing_fields() -> None:
    """Returns missing field names."""
    load_template_registry.cache_clear()
    missing = validate_context("sprint_report", {
        "sprint_name": "Sprint 3",
        "team_name": "Alpha",
    })
    assert "project_name" in missing
    assert "planned_points" in missing
    load_template_registry.cache_clear()
