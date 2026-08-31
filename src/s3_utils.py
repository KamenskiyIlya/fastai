import logging
import mimetypes
from pathlib import Path

import aioboto3
from aiobotocore.config import AioConfig
from furl import furl

from env_settings import settings

HTML_PATH = Path(__file__).resolve().parent.parent

_s3_config = AioConfig(
    max_pool_connections=settings.s3.max_pool_connections,
    connect_timeout=settings.s3.connect_timeout,
    read_timeout=settings.s3.read_timeout,
)

_s3_session = aioboto3.Session(
    aws_access_key_id=settings.s3.access_key.get_secret_value(),
    aws_secret_access_key=settings.s3.secret_key.get_secret_value(),
    region_name=settings.s3.region_name,
)


def get_mime_type(filename: str) -> str | None:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


async def upload_file(filename: str) -> str:
    try:
        body = (HTML_PATH / filename).read_bytes()
        async with _s3_session.client(  # type: ignore
            "s3",
            endpoint_url=settings.s3.bucket_url,
            config=_s3_config,
        ) as client:
            await client.put_object(
                Bucket=settings.s3.bucket_name,
                Key=filename,
                Body=body,
                ContentType=get_mime_type(filename),
                ContentDisposition="inline",
            )
            return (
                f"{settings.s3.bucket_url}/{settings.s3.bucket_name}"
                f"/{filename}"
            )
    except Exception:
        logging.error("Ошибка загрузки в bucket", exc_info=True)
        raise


def make_public_url(filename: str) -> str:
    return f"{settings.s3.bucket_url}/{settings.s3.bucket_name}/{filename}"


def make_download_url(base_url: str, filename: str) -> str:
    url = furl(base_url)
    url.args["response-content-disposition"] = (
        f'attachment; filename="{filename}"'
    )
    return str(url)


def get_site_urls() -> tuple[str, str, str]:
    open_url = make_public_url("index.html")
    download_url = make_download_url(open_url, "index.html")
    screenshot_url = make_public_url("index.png")
    return open_url, download_url, screenshot_url
