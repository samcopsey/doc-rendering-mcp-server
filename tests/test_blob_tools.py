"""Tests for Azure Blob Storage tools."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doc_rendering_mcp_server.tools.blob_tools import build_blob_name, upload_blob, upload_bytes_blob


class TestBlobNamingConvention:
    """Tests for the blob naming convention."""

    def test_blob_name_from_file_path(self) -> None:
        """Blob name derived from file path follows convention."""
        name = build_blob_name("/tmp/sprint_report.pdf", doc_type="sprint_report")
        date_str = datetime.now(tz=UTC).strftime("%Y-%m-%d")

        assert name.startswith(f"sprint_report/{date_str}/sprint_report_")
        assert name.endswith(".pdf")
        match = re.search(r"_([a-f0-9]{6})\.pdf$", name)
        assert match is not None

    def test_blob_name_without_file_path(self) -> None:
        """Blob name without file path uses doc_type and ext."""
        name = build_blob_name(None, doc_type="user_guide", ext="docx")
        date_str = datetime.now(tz=UTC).strftime("%Y-%m-%d")

        assert name.startswith(f"user_guide/{date_str}/user_guide_")
        assert name.endswith(".docx")

    def test_blob_name_unique(self) -> None:
        """Each call produces a unique blob name."""
        names = {build_blob_name("/tmp/test.pdf", doc_type="test") for _ in range(10)}
        assert len(names) == 10


@pytest.mark.asyncio
async def test_upload_blob(tmp_path) -> None:
    """upload_blob uploads file and returns SAS URL."""
    test_file = tmp_path / "report.pdf"
    test_file.write_bytes(b"%PDF-1.4 fake content")

    mock_blob_client = AsyncMock()
    mock_container_client = MagicMock()
    mock_container_client.get_blob_client = MagicMock(return_value=mock_blob_client)

    mock_delegation_key = MagicMock()

    mock_service_client = AsyncMock()
    mock_service_client.get_user_delegation_key = AsyncMock(return_value=mock_delegation_key)
    mock_service_client.get_container_client = MagicMock(return_value=mock_container_client)
    mock_service_client.__aenter__ = AsyncMock(return_value=mock_service_client)
    mock_service_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("doc_rendering_mcp_server.tools.blob_tools.get_blob_service_client", return_value=mock_service_client),
        patch("doc_rendering_mcp_server.tools.blob_tools.generate_blob_sas", return_value="sv=2024-01-01&sig=fakesig"),
    ):
        result = await upload_blob(str(test_file), content_type="application/pdf", doc_type="sprint_report")

    assert "url" in result
    assert "expires_at" in result
    assert "blob_name" in result
    assert "stcastdevdocs.blob.core.windows.net" in result["url"]
    assert "sv=2024-01-01" in result["url"]
    mock_blob_client.upload_blob.assert_called_once()


@pytest.mark.asyncio
async def test_upload_bytes_blob() -> None:
    """upload_bytes_blob uploads bytes content with correct content_type."""
    mock_blob_client = AsyncMock()
    mock_container_client = MagicMock()
    mock_container_client.get_blob_client = MagicMock(return_value=mock_blob_client)

    mock_delegation_key = MagicMock()

    mock_service_client = AsyncMock()
    mock_service_client.get_user_delegation_key = AsyncMock(return_value=mock_delegation_key)
    mock_service_client.get_container_client = MagicMock(return_value=mock_container_client)
    mock_service_client.__aenter__ = AsyncMock(return_value=mock_service_client)
    mock_service_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("doc_rendering_mcp_server.tools.blob_tools.get_blob_service_client", return_value=mock_service_client),
        patch("doc_rendering_mcp_server.tools.blob_tools.generate_blob_sas", return_value="sv=2024-01-01&sig=fakesig"),
    ):
        result = await upload_bytes_blob(
            data=b"<html><body>Report</body></html>",
            blob_name="sprint_report/2026-03-11/report_abc123.html",
            content_type="text/html",
        )

    assert "url" in result
    assert "expires_at" in result
    mock_blob_client.upload_blob.assert_called_once()


@pytest.mark.asyncio
async def test_upload_blob_error_handling(tmp_path) -> None:
    """upload_blob returns structured error on failure."""
    test_file = tmp_path / "report.pdf"
    test_file.write_bytes(b"%PDF-1.4 fake content")

    mock_service_client = AsyncMock()
    mock_service_client.__aenter__ = AsyncMock(return_value=mock_service_client)
    mock_service_client.__aexit__ = AsyncMock(return_value=None)
    mock_service_client.get_user_delegation_key = AsyncMock(side_effect=Exception("Auth failed"))

    with patch("doc_rendering_mcp_server.tools.blob_tools.get_blob_service_client", return_value=mock_service_client):
        result = await upload_blob(str(test_file), content_type="application/pdf")

    assert "error" in result
    assert "Failed to upload" in result["error"]


@pytest.mark.asyncio
async def test_upload_blob_not_configured(monkeypatch, tmp_path) -> None:
    """upload_blob returns error when storage account not configured."""
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "")

    test_file = tmp_path / "report.pdf"
    test_file.write_bytes(b"%PDF-1.4 fake content")

    result = await upload_blob(str(test_file))

    assert "error" in result
    assert "not configured" in result["error"]
