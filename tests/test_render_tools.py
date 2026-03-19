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
async def test_render_html_functional_spec() -> None:
    """Renders functional spec HTML with all 10 section headings."""
    load_template_registry.cache_clear()
    html = await _render_html("functional_spec", {
        "title": "Phoenix Spec Test",
        "project_name": "Cast",
        "overview": "A layman's overview of the system.",
        "problem_statement": "Manual processes waste engineering time.",
        "requirements": [
            {"id": "FR-001", "category": "Auth", "description": "SSO login", "priority": "Must Have"},
            {"id": "FR-002", "category": "Data", "description": "Export CSV", "priority": "Should Have"},
        ],
        "roi_questions": [
            "What is the current cost of manual processing?",
            "How many hours per week are spent on this task?",
        ],
        "growth_strategy_alignment": "Aligns with Efficiency pillar.",
        "problem_who_impacted": ["Engineering team", "Product managers"],
        "problem_current_state": "Everything is manual.",
        "problem_desired_state": "Fully automated pipeline.",
        "key_features": [
            {
                "name": "Auto-Sync",
                "capabilities": ["Real-time sync", "Conflict resolution"],
                "user_benefits": "No manual data entry",
            },
        ],
        "architecture_overview": "Microservice architecture on Azure.",
        "architecture_components": [
            {"component": "API Gateway", "technology": "Azure APIM", "purpose": "Request routing"},
        ],
        "nonfunctional_requirements": {"Performance": ["Response time < 200ms"], "Availability": "99.9% SLA"},
        "security_auth": "Microsoft Entra ID with MSAL.",
        "security_data_residency": "All data in UK South.",
        "systems_infrastructure": [
            {"service": "PostgreSQL", "environment": "Dev/Prod", "configuration": "B1ms flexible server"},
        ],
        "dependencies_technical": ["Azure subscription", "Entra ID tenant"],
        "implementation_phases": ["Phase 1: Foundation", "Phase 2: Core features", "Phase 3: Polish"],
        "target_go_live": "Q2 2026",
        "pre_delivery_checklist": ["UK English verified", "Security review complete"],
    })
    assert "Phoenix Spec Test" in html
    assert "1. Overview" in html
    assert "2. ROI Statement" in html
    assert "3. Problem Statement" in html
    assert "4. Key Features" in html
    assert "5. Functional Architecture" in html
    assert "6. Detailed Requirements" in html
    assert "7. Security" in html
    assert "8. Systems" in html
    assert "9. Dependencies" in html
    assert "10. Implementation Approach" in html
    assert "FR-001" in html
    assert "never be fabricated" in html
    assert "Pre-Delivery Checklist" in html
    load_template_registry.cache_clear()


@pytest.mark.asyncio
async def test_render_markdown_functional_spec() -> None:
    """Renders functional spec markdown with YAML frontmatter and section headings."""
    load_template_registry.cache_clear()
    md = await _render_markdown("functional_spec", {
        "title": "Phoenix Spec Test",
        "project_name": "Cast",
        "overview": "A layman's overview.",
        "problem_statement": "Manual processes are slow.",
        "requirements": [
            {"id": "FR-001", "description": "Must authenticate via SSO"},
        ],
        "roi_questions": ["What is the current cost?"],
        "security_auth": "Entra ID.",
        "implementation_phases": ["Phase 1: Build", "Phase 2: Deploy"],
    })
    assert "title:" in md
    assert "## 1. Overview" in md
    assert "## 3. Problem Statement" in md
    assert "## 6. Detailed Requirements" in md
    assert "FR-001" in md
    assert "never be fabricated" in md
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
