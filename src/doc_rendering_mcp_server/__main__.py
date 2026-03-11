"""Allow running as `python -m doc_rendering_mcp_server`."""

import os

import uvicorn

from doc_rendering_mcp_server.server import app

port = int(os.environ.get("MCP_SERVER_PORT", "3001"))
uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
