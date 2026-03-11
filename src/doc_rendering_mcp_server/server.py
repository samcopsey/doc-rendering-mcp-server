"""Doc Rendering MCP Server — Streamable HTTP transport."""

from __future__ import annotations

import contextlib

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from doc_rendering_mcp_server.tools.render_tools import register_tools as register_render_tools
from doc_rendering_mcp_server.tools.template_tools import register_tools as register_template_tools


def _create_mcp() -> FastMCP:
    """Create a fresh FastMCP instance with tools registered."""
    mcp = FastMCP(
        "doc-rendering-mcp-server",
        stateless_http=True,
        json_response=True,
        # Disable DNS rebinding protection — runs behind Container Apps ingress proxy.
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
    register_template_tools(mcp)
    register_render_tools(mcp)
    return mcp


def create_app() -> Starlette:
    """Create the ASGI app with health and MCP routes."""
    mcp = _create_mcp()

    async def health(request: Request) -> JSONResponse:
        tools = list(mcp._tool_manager._tools.keys())
        return JSONResponse({"status": "ok", "server": "doc-rendering-mcp-server", "tools": tools})

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with mcp.session_manager.run():
            yield

    mcp_app = mcp.streamable_http_app()
    routes = [
        Route("/", health),
        Route("/health", health),
        *mcp_app.routes,
    ]
    return Starlette(routes=routes, lifespan=lifespan)


app = create_app()
