FROM python:3.11-slim

# WeasyPrint system dependencies (pango, cairo, gdk-pixbuf)
# libgdk-pixbuf-2.0-0 replaces libgdk-pixbuf2.0-0 in Debian Trixie (python:3.11-slim)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
    libffi-dev libcairo2 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir .

EXPOSE 3001

CMD ["python", "-m", "doc_rendering_mcp_server"]
