import asyncio
import logging
from pathlib import Path

import aioboto3
from aiobotocore.config import AioConfig
from furl import furl

from env_settings import settings

HTML_PATH = Path(__file__).resolve().parent.parent


async def upload_html(filename: str) -> str:
    config = AioConfig(
        max_pool_connections=10,
        connect_timeout=20,
        read_timeout=30,
    )
    session = aioboto3.Session(
        aws_access_key_id=settings.s3.access_key.get_secret_value(),
        aws_secret_access_key=settings.s3.secret_key.get_secret_value(),
        region_name=settings.s3.region_name,
    )
    try:
        html = (HTML_PATH / filename).read_text(encoding="utf-8")
        async with session.client(  # type: ignore
            "s3",
            endpoint_url=settings.s3.bucket_url,
            config=config,
        ) as client:
            await client.put_object(
                Bucket=settings.s3.bucket_name,
                Key=filename,
                Body=html,
                ContentType="text/html",
                ContentDisposition="inline",
            )
            return (
                f"{settings.s3.bucket_url}/{settings.s3.bucket_name}"
                f"/{filename}"
            )
    except Exception as exc:
        logging.error(f"Ошибка загрузки в bucket: {exc}")
        raise


def make_download_url(base_url: str, filename: str) -> str:
    url = furl(base_url)
    url.args["response-content-disposition"] = (
        f'attachment; filename="{filename}"'
    )
    return str(url)


def main():
    open_url = asyncio.run(upload_html("index.html"))
    download_url = make_download_url(open_url, "index.html")

    print(f"Открыть сайт: {open_url}")
    print(f"Скачать сайт: {download_url}")


if __name__ == "__main__":
    main()
