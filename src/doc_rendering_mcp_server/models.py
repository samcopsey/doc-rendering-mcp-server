"""Pydantic models for the template registry."""

from __future__ import annotations

from pydantic import BaseModel


class TemplateFormat(BaseModel):
    """A single format variant of a template."""

    template: str
    css: str | None = None
    version: str = "1.0"


class TemplateEntry(BaseModel):
    """A registered document template."""

    display_name: str
    description: str
    category: str
    formats: dict[str, TemplateFormat]
    required_fields: list[str]
    optional_fields: list[str] = []
    default_publish_target: str = "wiki"


class TemplateRegistry(BaseModel):
    """Root model for templates.yaml."""

    version: str
    templates: dict[str, TemplateEntry]
