"""Template registry tools — list templates and validate context."""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import structlog
import yaml
from mcp.server.fastmcp import FastMCP

from doc_rendering_mcp_server.models import TemplateRegistry

logger = structlog.get_logger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@functools.lru_cache(maxsize=1)
def load_template_registry() -> TemplateRegistry:
    """Parse templates.yaml and return the registry.

    Returns:
        TemplateRegistry with all registered templates.

    Raises:
        FileNotFoundError: If templates.yaml does not exist.
    """
    registry_path = TEMPLATES_DIR / "templates.yaml"
    if not registry_path.exists():
        raise FileNotFoundError(f"Template registry not found: {registry_path}")

    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    registry = TemplateRegistry(**raw)
    logger.info("template_registry_loaded", template_count=len(registry.templates))
    return registry


def get_template_info(template_name: str) -> Any:
    """Return registry entry for a template.

    Args:
        template_name: Template key (e.g. 'sprint_report').

    Returns:
        TemplateEntry for the template.

    Raises:
        KeyError: If template is not in the registry.
    """
    registry = load_template_registry()
    if template_name not in registry.templates:
        available = list(registry.templates.keys())
        raise KeyError(f"Template '{template_name}' not found. Available: {available}")
    return registry.templates[template_name]


def validate_context(template_name: str, context: dict[str, Any]) -> list[str]:
    """Check that required fields are present in the context.

    Args:
        template_name: Template key.
        context: Context dict to validate.

    Returns:
        List of missing required field names. Empty if all present.
    """
    entry = get_template_info(template_name)
    return [f for f in entry.required_fields if f not in context or context[f] is None]


def register_tools(mcp: FastMCP) -> None:
    """Register template tools on the MCP server."""

    @mcp.tool()
    async def list_templates() -> list[dict[str, Any]]:
        """List all available document templates with names, descriptions, formats, and required fields."""
        registry = load_template_registry()
        results = []
        for name, entry in registry.templates.items():
            # PDF is derived from HTML via WeasyPrint — advertise it for any template with HTML
            formats = list(entry.formats.keys())
            if "html" in formats and "pdf" not in formats:
                formats.append("pdf")
            results.append({
                "name": name,
                "display_name": entry.display_name,
                "description": entry.description,
                "category": entry.category,
                "formats": formats,
                "required_fields": entry.required_fields,
                "optional_fields": entry.optional_fields,
            })
        return results

    @mcp.tool()
    async def validate_template_context(template_name: str, context: dict[str, Any]) -> dict[str, Any]:
        """Validate that all required fields are present for a given template.

        Args:
            template_name: Template key (e.g. 'sprint_report', 'user_guide').
            context: Context variables to validate against the template's required fields.

        Returns:
            Dict with 'valid' (bool) and 'missing_fields' (list of field names).
        """
        try:
            missing = validate_context(template_name, context)
            return {"valid": len(missing) == 0, "missing_fields": missing}
        except KeyError as e:
            return {"valid": False, "error": str(e)}
