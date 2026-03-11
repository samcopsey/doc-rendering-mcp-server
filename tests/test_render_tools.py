"""Tests for document rendering tools."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from doc_rendering_mcp_server.models import TemplateEntry, TemplateFormat
from doc_rendering_mcp_server.tools.render_tools import _render_html, _render_markdown
from doc_rendering_mcp_server.tools.template_tools import load_template_registry


@pytest.mark.asyncio
async def test_render_html_sprint_report() -> None:
    """Renders sprint report HTML with correct content."""
    load_template_registry.cache_clear()
    html = await _render_html("sprint_report", {
        "title": "Sprint Report: Sprint 3",
        "sprint_name": "Sprint 3",
        "team_name": "Alpha Team",
        "project_name": "Cast",
        "start_date": "2026-03-01",
        "end_date": "2026-03-14",
        "planned_points": 30,
        "completed_points": 25,
        "velocity": 25,
        "completion_rate": 83,
    })
    assert "Sprint 3" in html
    assert "Alpha Team" in html
    assert "Cast" in html
    assert "<html" in html
    load_template_registry.cache_clear()


@pytest.mark.asyncio
async def test_render_html_use_case() -> None:
    """Renders use case HTML with actors table."""
    load_template_registry.cache_clear()
    html = await _render_html("use_case", {
        "title": "Login Use Case",
        "project_name": "Cast",
        "overview": "User authentication flow.",
        "actors": [
            {"name": "End User", "description": "A person logging in"},
            {"name": "System", "description": "The Cast platform"},
        ],
        "main_flow": ["User enters credentials", "System validates", "User sees dashboard"],
    })
    assert "Login Use Case" in html
    assert "End User" in html
    assert "credentials" in html
    load_template_registry.cache_clear()


@pytest.mark.asyncio
async def test_render_html_no_format_raises() -> None:
    """Raises FileNotFoundError for template without HTML format."""
    load_template_registry.cache_clear()

    with patch("doc_rendering_mcp_server.tools.render_tools.get_template_info") as mock:
        mock.return_value = TemplateEntry(
            display_name="Test",
            description="Test template",
            category="test",
            formats={"docx": TemplateFormat(template="docx/test.docx")},
            required_fields=["title"],
        )
        with pytest.raises(FileNotFoundError, match="no HTML format"):
            await _render_html("test_template", {"title": "Test"})
    load_template_registry.cache_clear()


@pytest.mark.asyncio
async def test_render_markdown_sprint_report() -> None:
    """Renders sprint report markdown with Jinja2."""
    load_template_registry.cache_clear()
    md = await _render_markdown("sprint_report", {
        "sprint_name": "Sprint 3",
        "team_name": "Alpha Team",
        "project_name": "Cast",
        "start_date": "2026-03-01",
        "end_date": "2026-03-14",
        "planned_points": 30,
        "completed_points": 25,
        "velocity": 25,
        "completion_rate": 83,
        "summary": "Good sprint overall.",
        "completed_items": "- Item 1\n- Item 2",
        "carried_over_items": "None",
        "capacity_summary": "Full capacity",
        "retrospective_notes": "Keep it up",
        "generated_date": "2026-03-15",
    })
    assert "Sprint 3" in md
    assert "Alpha Team" in md
    assert "Good sprint overall." in md
    load_template_registry.cache_clear()


@pytest.mark.asyncio
async def test_render_markdown_no_format_raises() -> None:
    """Raises FileNotFoundError for template without markdown format."""
    load_template_registry.cache_clear()

    with patch("doc_rendering_mcp_server.tools.render_tools.get_template_info") as mock:
        mock.return_value = TemplateEntry(
            display_name="Test",
            description="Test template",
            category="test",
            formats={"html": TemplateFormat(template="html/base.html")},
            required_fields=["title"],
        )
        with pytest.raises(FileNotFoundError, match="no Markdown format"):
            await _render_markdown("test_template", {"title": "Test"})
    load_template_registry.cache_clear()


@pytest.mark.asyncio
async def test_render_pdf_sprint_report() -> None:
    """Renders sprint report as PDF (conditional — requires WeasyPrint)."""
    try:
        from weasyprint import HTML  # noqa: F401
    except (ImportError, OSError):
        pytest.skip("WeasyPrint not available")

    from unittest.mock import AsyncMock

    from doc_rendering_mcp_server.tools.render_tools import _render_pdf

    load_template_registry.cache_clear()

    mock_upload = AsyncMock(return_value={
        "blob_name": "sprint_report/2026-03-11/sprint_report_abc123.pdf",
        "url": "https://stcastdevdocs.blob.core.windows.net/documents/sprint_report.pdf?sv=2024&sig=fake",
        "expires_at": "2026-03-11T13:00:00+00:00",
    })

    with patch("doc_rendering_mcp_server.tools.render_tools.upload_blob", mock_upload):
        result = await _render_pdf("sprint_report", {
            "title": "Sprint Report: Sprint 3",
            "sprint_name": "Sprint 3",
            "team_name": "Alpha",
            "project_name": "Cast",
            "start_date": "2026-03-01",
            "end_date": "2026-03-14",
            "planned_points": 30,
            "completed_points": 25,
            "velocity": 25,
        })

    assert "download_url" in result
    assert "expires_at" in result
    mock_upload.assert_called_once()
    load_template_registry.cache_clear()
