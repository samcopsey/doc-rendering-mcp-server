# Doc Rendering MCP Server

> MCP server for document rendering — templates, HTML/PDF/DOCX/Markdown, Azure Blob Storage delivery.

Part of the [Cast](https://github.com/samcopsey/cast-ado-agent) multi-agent system. Provides document rendering capabilities to Foundry agents via MCP tools.

## Why a Separate Server?

Foundry agents deployed via `PromptAgentDefinition` have **no Python runtime** — only MCP tools are available. The doc generator agent needs real rendering capabilities (HTML templates, WeasyPrint PDF, docxtpl DOCX), so these are extracted into this MCP server. The agent connects to it via a Foundry MCP connection.

## Tools

| Tool | Returns | Description |
|------|---------|-------------|
| `list_templates` | JSON array | All available templates with metadata, formats, required fields |
| `validate_template_context` | `{valid, missing_fields}` | Check required fields before rendering |
| `render_html` | HTML string | Render template as HTML |
| `render_pdf` | `{download_url, expires_at}` | Render HTML→PDF via WeasyPrint, upload to Blob Storage |
| `render_docx` | `{download_url, expires_at}` | Render docxtpl template, upload to Blob Storage |
| `render_markdown` | Markdown string | Render template as Markdown |

Binary formats (PDF/DOCX) automatically upload to Azure Blob Storage and return a time-limited SAS download URL (1 hour). Text formats (HTML/Markdown) return content directly.

## Templates

Built-in templates:

- **user_guide** — step-by-step end-user instructions (HTML/PDF, DOCX)
- **use_case** — structured use case with actors and flows (HTML/PDF, Markdown)
- **sprint_report** — sprint velocity and completion summary (HTML/PDF, Markdown)
- **functional_spec** — detailed functional specification (HTML/PDF, DOCX)

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Docker | latest |
| Azure CLI | 2.x |

## Local Development

```bash
# Set up environment
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/

# Run locally
export AZURE_STORAGE_ACCOUNT_NAME=stcastdevdocs
az login
python -m doc_rendering_mcp_server
# Server starts on http://localhost:3001
# MCP endpoint: http://localhost:3001/mcp
# Health: http://localhost:3001/health
```

## Deployment (Container Apps)

```bash
# From the cast-ado-agent infra directory
ACR_NAME=$(terraform output -raw acr_name)
ACR_SERVER=$(terraform output -raw acr_login_server)
az acr login --name $ACR_NAME

# Build and push
cd /path/to/doc-rendering-mcp-server
docker build --platform linux/amd64 -t $ACR_SERVER/doc-rendering-mcp-server:v0.1.0 .
docker push $ACR_SERVER/doc-rendering-mcp-server:v0.1.0

# Deploy via Terraform
cd /path/to/cast-ado-agent/infra
terraform apply -var-file=environments/dev.tfvars -var='doc_rendering_mcp_image_tag=v0.1.0'
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_STORAGE_ACCOUNT_NAME` | Yes | — | Storage account for document blob delivery |
| `AZURE_STORAGE_CONTAINER_NAME` | No | `documents` | Blob container name |
| `MCP_SERVER_PORT` | No | `3001` | Server port |
| `LOG_LEVEL` | No | `info` | Log level |

Auth uses `DefaultAzureCredential` — Managed Identity on Container Apps, `az login` locally.

## Foundry Connection

After deploying to Container Apps:

1. Open Foundry portal → cast-doc-generator agent
2. Add MCP connection pointing to `https://ca-doc-rendering-mcp-cast-dev.<region>.azurecontainerapps.io/mcp`
3. The agent's MCP tools (`list_templates`, `render_pdf`, etc.) are now available

## Licence

MIT
