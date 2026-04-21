import uuid
from datetime import timedelta
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_s3_client = None


def get_storage_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT_URL,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION,
        )
    return _s3_client


def build_storage_path(
    tenant_id: str,
    year: int,
    month: int,
    provider: str,
    filename: str,
) -> str:
    """Build canonical storage path: tenant/{id}/year/{yyyy}/month/{mm}/source/{provider}/{file}"""
    return f"tenant/{tenant_id}/year/{year:04d}/month/{month:02d}/source/{provider}/{filename}"


def upload_file(
    bucket: str,
    key: str,
    file_obj: BinaryIO,
    content_type: str = "application/octet-stream",
) -> str:
    client = get_storage_client()
    client.upload_fileobj(
        file_obj,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    logger.info("file_uploaded", bucket=bucket, key=key)
    return key


def generate_presigned_url(bucket: str, key: str, expiry_seconds: int = 900) -> str:
    """Generate a signed URL valid for expiry_seconds (default 15 min)."""
    client = get_storage_client()
    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expiry_seconds,
    )
    return url


def download_file_bytes(bucket: str, key: str) -> bytes:
    client = get_storage_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()
