"""Azure Blob Storage tools — upload rendered documents and generate SAS download URLs."""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import structlog
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.blob.aio import BlobServiceClient

logger = structlog.get_logger(__name__)


def _get_storage_account_name() -> str:
    """Get storage account name from environment."""
    return os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")


def _get_container_name() -> str:
    """Get container name from environment."""
    return os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "documents")


def build_blob_name(file_path: str | None, doc_type: str = "general", ext: str = "bin") -> str:
    """Build a blob name following the convention: {doc_type}/{date}/{name}_{uuid_short}.{ext}.

    Args:
        file_path: Optional source file path to derive name/extension from.
        doc_type: Document type category (e.g. 'sprint_report', 'user_guide').
        ext: File extension (used if file_path not provided).

    Returns:
        Blob name string.
    """
    date_str = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    short_id = uuid.uuid4().hex[:6]

    if file_path:
        p = Path(file_path)
        name = p.stem
        ext = p.suffix.lstrip(".")
    else:
        name = doc_type

    return f"{doc_type}/{date_str}/{name}_{short_id}.{ext}"


def get_blob_service_client() -> BlobServiceClient:
    """Create a BlobServiceClient using DefaultAzureCredential.

    Returns:
        Configured BlobServiceClient.
    """
    account_name = _get_storage_account_name()
    account_url = f"https://{account_name}.blob.core.windows.net"
    credential = DefaultAzureCredential()
    return BlobServiceClient(account_url=account_url, credential=credential)


async def _get_user_delegation_key(client: BlobServiceClient) -> Any:
    """Get a user delegation key for SAS generation.

    Args:
        client: BlobServiceClient instance.

    Returns:
        UserDelegationKey valid for 2 hours.
    """
    now = datetime.now(tz=UTC)
    return await client.get_user_delegation_key(
        key_start_time=now,
        key_expiry_time=now + timedelta(hours=2),
    )


def _generate_sas_url(
    account_name: str,
    container_name: str,
    blob_name: str,
    user_delegation_key: Any,
    expiry_hours: int = 1,
) -> tuple[str, str]:
    """Generate a SAS URL for a blob using a user delegation key.

    Args:
        account_name: Storage account name.
        container_name: Container name.
        blob_name: Blob name within the container.
        user_delegation_key: User delegation key.
        expiry_hours: Hours until the SAS expires.

    Returns:
        Tuple of (full SAS URL, expiry ISO timestamp).
    """
    expiry = datetime.now(tz=UTC) + timedelta(hours=expiry_hours)
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        user_delegation_key=user_delegation_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
    )
    url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    return url, expiry.isoformat()


async def upload_blob(
    file_path: str,
    blob_name: str | None = None,
    content_type: str = "application/octet-stream",
    doc_type: str = "general",
    expiry_hours: int = 1,
) -> dict[str, str]:
    """Upload a local file to blob storage and return a SAS download URL.

    Args:
        file_path: Path to the local file to upload.
        blob_name: Optional blob name (auto-generated if not provided).
        content_type: MIME type of the file.
        doc_type: Document type for blob naming convention.
        expiry_hours: Hours until the download URL expires.

    Returns:
        Dict with 'blob_name', 'url', and 'expires_at'.
    """
    account_name = _get_storage_account_name()
    container_name = _get_container_name()

    if not account_name:
        return {"error": "Azure Storage account not configured (AZURE_STORAGE_ACCOUNT_NAME is empty)"}

    if not blob_name:
        blob_name = build_blob_name(file_path, doc_type=doc_type)

    try:
        async with get_blob_service_client() as client:
            delegation_key = await _get_user_delegation_key(client)

            container_client = client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)

            file_data = Path(file_path).read_bytes()
            await blob_client.upload_blob(
                file_data,
                content_settings={"content_type": content_type},
                overwrite=True,
            )

            url, expires_at = _generate_sas_url(
                account_name=account_name,
                container_name=container_name,
                blob_name=blob_name,
                user_delegation_key=delegation_key,
                expiry_hours=expiry_hours,
            )

        logger.info(
            "blob_uploaded",
            blob_name=blob_name,
            content_type=content_type,
            file_path=file_path,
            expires_at=expires_at,
        )
        return {"blob_name": blob_name, "url": url, "expires_at": expires_at}

    except Exception:
        logger.exception("blob_upload_failed", file_path=file_path, blob_name=blob_name)
        return {"error": f"Failed to upload {file_path} to blob storage. Check logs for details."}


async def upload_bytes_blob(
    data: bytes,
    blob_name: str,
    content_type: str = "application/octet-stream",
    expiry_hours: int = 1,
) -> dict[str, str]:
    """Upload bytes to blob storage and return a SAS download URL.

    Args:
        data: Bytes to upload.
        blob_name: Blob name within the container.
        content_type: MIME type of the content.
        expiry_hours: Hours until the download URL expires.

    Returns:
        Dict with 'blob_name', 'url', and 'expires_at'.
    """
    account_name = _get_storage_account_name()
    container_name = _get_container_name()

    if not account_name:
        return {"error": "Azure Storage account not configured (AZURE_STORAGE_ACCOUNT_NAME is empty)"}

    try:
        async with get_blob_service_client() as client:
            delegation_key = await _get_user_delegation_key(client)

            container_client = client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)

            await blob_client.upload_blob(
                data,
                content_settings={"content_type": content_type},
                overwrite=True,
            )

            url, expires_at = _generate_sas_url(
                account_name=account_name,
                container_name=container_name,
                blob_name=blob_name,
                user_delegation_key=delegation_key,
                expiry_hours=expiry_hours,
            )

        logger.info("bytes_blob_uploaded", blob_name=blob_name, content_type=content_type, expires_at=expires_at)
        return {"blob_name": blob_name, "url": url, "expires_at": expires_at}

    except Exception:
        logger.exception("bytes_blob_upload_failed", blob_name=blob_name)
        return {"error": f"Failed to upload blob {blob_name}. Check logs for details."}
