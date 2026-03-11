"""Document rendering tools — HTML, PDF, DOCX, and Markdown generation via MCP."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import structlog
from jinja2 import Environment, FileSystemLoader
from mcp.server.fastmcp import FastMCP

from doc_rendering_mcp_server.tools.blob_tools import build_blob_name, upload_blob
from doc_rendering_mcp_server.tools.template_tools import TEMPLATES_DIR, get_template_info

logger = structlog.get_logger(__name__)


def _get_jinja_env() -> Environment:
    """Create a Jinja2 Environment for HTML template rendering."""
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


async def _render_html(template_name: str, context: dict[str, Any]) -> str:
    """Render an HTML document from a registered template.

    Args:
        template_name: Template key.
        context: Jinja2 context variables.

    Returns:
        Rendered HTML string.
    """
    entry = get_template_info(template_name)
    if "html" not in entry.formats:
        raise FileNotFoundError(f"Template '{template_name}' has no HTML format. Available: {list(entry.formats.keys())}")

    env = _get_jinja_env()
    template = env.get_template(entry.formats["html"].template)
    html = template.render(**context)
    logger.info("rendered_html", template=template_name, length=len(html))
    return html


async def _render_pdf(template_name: str, context: dict[str, Any]) -> dict[str, str]:
    """Render HTML→PDF via WeasyPrint, upload to blob storage, return SAS URL.

    Args:
        template_name: Template key.
        context: Jinja2 context variables.

    Returns:
        Dict with 'download_url' and 'expires_at'.
    """
    from weasyprint import HTML

    html_string = await _render_html(template_name, context)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / f"{template_name}.pdf"
        HTML(string=html_string, base_url=str(TEMPLATES_DIR)).write_pdf(str(output_path))
        logger.info("rendered_pdf", template=template_name, output=str(output_path))

        result = await upload_blob(
            str(output_path),
            content_type="application/pdf",
            doc_type=template_name,
        )

    if "error" in result:
        return {"error": result["error"]}
    return {"download_url": result["url"], "expires_at": result["expires_at"]}


async def _render_docx(template_name: str, context: dict[str, Any]) -> dict[str, str]:
    """Render a DOCX document from a docxtpl template, upload to blob, return SAS URL.

    Args:
        template_name: Template key.
        context: Jinja2 context variables.

    Returns:
        Dict with 'download_url' and 'expires_at'.
    """
    from docxtpl import DocxTemplate

    entry = get_template_info(template_name)
    if "docx" not in entry.formats:
        raise FileNotFoundError(
            f"Template '{template_name}' has no DOCX format. Available: {list(entry.formats.keys())}"
        )

    template_path = TEMPLATES_DIR / entry.formats["docx"].template
    if not template_path.exists():
        raise FileNotFoundError(f"DOCX template file not found: {template_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / f"{template_name}.docx"
        doc = DocxTemplate(str(template_path))
        doc.render(context)
        doc.save(str(output_path))
        logger.info("rendered_docx", template=template_name, output=str(output_path))

        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        result = await upload_blob(
            str(output_path),
            content_type=content_type,
            doc_type=template_name,
        )

    if "error" in result:
        return {"error": result["error"]}
    return {"download_url": result["url"], "expires_at": result["expires_at"]}


async def _render_markdown(template_name: str, context: dict[str, Any]) -> str:
    """Render a Markdown document from a Jinja2 template.

    Args:
        template_name: Template key.
        context: Template variables.

    Returns:
        Rendered Markdown string.
    """
    entry = get_template_info(template_name)
    if "markdown" not in entry.formats:
        raise FileNotFoundError(
            f"Template '{template_name}' has no Markdown format. Available: {list(entry.formats.keys())}"
        )

    template_path = TEMPLATES_DIR / entry.formats["markdown"].template
    if not template_path.exists():
        raise FileNotFoundError(f"Markdown template not found: {template_path}")

    env = _get_jinja_env()
    template = env.get_template(entry.formats["markdown"].template)
    rendered = template.render(**context)
    logger.info("rendered_markdown", template=template_name, length=len(rendered))
    return rendered


def register_tools(mcp: FastMCP) -> None:
    """Register rendering tools on the MCP server."""

    @mcp.tool()
    async def render_html(template_name: str, context: dict[str, Any]) -> str:
        """Render an HTML document from a registered template. Returns HTML string.

        Args:
            template_name: Template key (e.g. 'sprint_report', 'user_guide', 'use_case', 'functional_spec').
            context: Template variables as a JSON object. Call list_templates to see required fields.
        """
        return await _render_html(template_name, context)

    @mcp.tool()
    async def render_pdf(template_name: str, context: dict[str, Any]) -> dict[str, str]:
        """Render a PDF document from a template. Automatically uploads to Azure Blob Storage and returns a time-limited download URL (1 hour).

        Args:
            template_name: Template key (e.g. 'sprint_report', 'user_guide', 'functional_spec').
            context: Template variables as a JSON object. Call list_templates to see required fields.
        """
        return await _render_pdf(template_name, context)

    @mcp.tool()
    async def render_docx(template_name: str, context: dict[str, Any]) -> dict[str, str]:
        """Render a DOCX (Word) document from a template. Automatically uploads to Azure Blob Storage and returns a time-limited download URL (1 hour).

        Args:
            template_name: Template key (e.g. 'user_guide', 'functional_spec').
            context: Template variables as a JSON object. Call list_templates to see required fields.
        """
        return await _render_docx(template_name, context)

    @mcp.tool()
    async def render_markdown(template_name: str, context: dict[str, Any]) -> str:
        """Render a Markdown document from a template. Returns Markdown string with YAML frontmatter.

        Args:
            template_name: Template key (e.g. 'sprint_report', 'use_case').
            context: Template variables as a JSON object. Call list_templates to see required fields.
        """
        return await _render_markdown(template_name, context)
