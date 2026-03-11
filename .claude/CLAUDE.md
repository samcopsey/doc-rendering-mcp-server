# CLAUDE.md — Doc Rendering MCP Server

## Project Overview

MCP server providing document rendering tools (HTML, PDF, DOCX, Markdown) with Azure Blob Storage delivery. Part of the Cast multi-agent system. Deployed on Azure Container Apps, connected to Foundry agents via MCP.

## Tech Stack

- **Language**: Python 3.11+
- **MCP**: `mcp[cli]` with FastMCP, Streamable HTTP transport
- **Server**: Starlette + uvicorn
- **Rendering**: Jinja2 (HTML/Markdown), WeasyPrint (PDF), docxtpl (DOCX)
- **Storage**: Azure Blob Storage with SAS URL delivery
- **Auth**: `DefaultAzureCredential` (Managed Identity on Container Apps)
- **Testing**: pytest, pytest-asyncio, respx

## Project Structure

```
doc-rendering-mcp-server/
├── src/doc_rendering_mcp_server/
│   ├── __init__.py
│   ├── __main__.py          # uvicorn entry point (port 3001)
│   ├── server.py            # FastMCP app with Starlette routes
│   ├── models.py            # Pydantic models (TemplateRegistry, TemplateEntry)
│   ├── tools/
│   │   ├── template_tools.py  # list_templates, validate_template_context
│   │   ├── render_tools.py    # render_html, render_pdf, render_docx, render_markdown
│   │   └── blob_tools.py     # upload + SAS URL generation
│   └── templates/             # Bundled in Docker image
│       ├── templates.yaml     # Template registry
│       ├── html/              # HTML Jinja2 templates
│       ├── css/               # Stylesheet
│       ├── markdown/          # Markdown Jinja2 templates
│       ├── docx/              # DOCX templates (docxtpl)
│       └── assets/            # Logo etc.
├── tests/
├── Dockerfile                 # Includes WeasyPrint system deps
└── pyproject.toml
```

## Coding Standards

- **Type hints** — `from __future__ import annotations` at top of every file
- **Async** — all tool functions use `async/await`
- **Error handling** — never let tool functions raise unhandled exceptions; return structured error dicts
- **Line length** — 120 characters max
- **Docstrings** — Google style on public functions

## Common Commands

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest tests/ -v
ruff check src/ tests/
python -m doc_rendering_mcp_server  # runs on port 3001
```

## Tool Reference

| Tool | Parameters | Returns |
|------|-----------|---------|
| `list_templates` | none | JSON array of template metadata |
| `validate_template_context` | `template_name`, `context` | `{valid, missing_fields}` |
| `render_html` | `template_name`, `context` | HTML string |
| `render_pdf` | `template_name`, `context` | `{download_url, expires_at}` |
| `render_docx` | `template_name`, `context` | `{download_url, expires_at}` |
| `render_markdown` | `template_name`, `context` | Markdown string |

## Key Patterns

- Follows `ado-mcp-server` patterns: FastMCP, Starlette, health endpoint, DNS rebinding disabled
- Templates bundled in Docker image (not fetched at runtime)
- Binary formats auto-upload to Blob Storage, return SAS URL
- Text formats return content directly
- Port 3001 (ado-mcp-server uses 3000)
