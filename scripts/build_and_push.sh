#!/usr/bin/env bash
# Build and push doc-rendering-mcp-server to ACR.
# Usage: ./scripts/build_and_push.sh v0.1.0
#
# Requires: Docker, Azure CLI (logged in), Terraform outputs from cast-ado-agent/infra

set -euo pipefail

VERSION="${1:?Usage: $0 <version-tag>}"
INFRA_DIR="${CAST_INFRA_DIR:-$(cd "$(dirname "$0")/../../cast-ado-agent/infra" && pwd)}"

ACR_NAME=$(cd "$INFRA_DIR" && terraform output -raw acr_name)
ACR_SERVER=$(cd "$INFRA_DIR" && terraform output -raw acr_login_server)

echo "Building doc-rendering-mcp-server:${VERSION}"
echo "ACR: ${ACR_SERVER}"

az acr login --name "$ACR_NAME"

docker build --platform linux/amd64 -t "${ACR_SERVER}/doc-rendering-mcp-server:${VERSION}" .
docker push "${ACR_SERVER}/doc-rendering-mcp-server:${VERSION}"

echo ""
echo "Image pushed: ${ACR_SERVER}/doc-rendering-mcp-server:${VERSION}"
echo ""
echo "Deploy via Terraform:"
echo "  cd ${INFRA_DIR}"
echo "  terraform apply -var-file=environments/dev.tfvars -var='doc_rendering_mcp_image_tag=${VERSION}'"
