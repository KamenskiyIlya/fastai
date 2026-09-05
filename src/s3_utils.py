import mimetypes
from pathlib import Path

from furl import furl
from pydantic import HttpUrl

from env_settings import settings

HTML_PATH = Path(__file__).resolve().parent.parent


def get_mime_type(filename: str) -> str | None:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


async def upload_file(s3_client, filename: str) -> str:
    body = (HTML_PATH / filename).read_bytes()
    await s3_client.put_object(
        Bucket=settings.s3.bucket_name,
        Key=filename,
        Body=body,
        ContentType=get_mime_type(filename),
        ContentDisposition="inline",
    )
    return f"{settings.s3.bucket_url}/{settings.s3.bucket_name}/{filename}"


def make_public_url(filename: str) -> HttpUrl:
    return HttpUrl(
        f"{settings.s3.bucket_url}/{settings.s3.bucket_name}/{filename}",
    )


def make_download_url(base_url: HttpUrl, filename: str) -> HttpUrl:
    url = furl(str(base_url))
    url.args["response-content-disposition"] = (
        f'attachment; filename="{filename}"'
    )
    return HttpUrl(str(url))
