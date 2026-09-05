import logging
from datetime import datetime

import anyio
import httpx
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from gotenberg_api import GotenbergServerError

from generator import html_generator, make_screenshot
from s3_utils import make_download_url, make_public_url, upload_file
from schemas import (
    CreateSiteRequest,
    GeneratedSitesResponse,
    SiteGenerationRequest,
    SiteResponse,
)

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get(
    "/my",
    response_model=GeneratedSitesResponse,
    summary="Получить список сгенерированных сайтов",
    tags=["Sites"],
)
def get_user_sites() -> GeneratedSitesResponse:
    html_code_url = make_public_url("index.html")
    html_download_url = make_download_url(html_code_url, "index.html")
    screenshot_url = make_public_url("index.png")
    site = SiteResponse(
        id=1,
        title="Фан клуб Домино",
        prompt="Сайт любителей играть в домино",
        html_code_url=html_code_url,
        html_code_download_url=html_download_url,
        screenshot_url=screenshot_url,
        created_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    )
    return GeneratedSitesResponse(sites=[site])


@router.post(
    "/create",
    response_model=SiteResponse,
    summary="Создать сайт",
)
def create_site(body: CreateSiteRequest) -> SiteResponse:
    html_code_url = make_public_url("index.html")
    html_download_url = make_download_url(html_code_url, "index.html")
    screenshot_url = make_public_url("index.png")
    return SiteResponse(
        id=1,
        title=body.title or "Фан клуб Домино",
        prompt=body.prompt,
        html_code_url=html_code_url,
        html_code_download_url=html_download_url,
        screenshot_url=screenshot_url,
        created_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    )


@router.post(
    "/{site_id}/generate",
    summary="Сгенерировать HTML разметку сайта",
    description="Код сайта будет транслироваться стримом по мере генерации.",
    response_class=PlainTextResponse,
)
async def generate_site(
    request: Request,
    site_id: int,
    body: SiteGenerationRequest,
):
    async def stream_and_upload():
        s3_client = request.app.state.s3_client
        gotenberg_client = request.app.state.gotenberg_client
        with anyio.CancelScope(shield=True):
            async for chunk in html_generator(body.prompt):
                yield chunk
            html_filename = "index.html"
            screenshot_filename = "index.png"
            try:
                await upload_file(s3_client, html_filename)
                logging.info("HTML файл успешно загружен в bucket")
            except (BotoCoreError, ClientError, FileNotFoundError):
                logging.error(
                    f"{html_filename} файл не был загружен в bucket",
                    exc_info=True,
                )
            try:
                await make_screenshot(gotenberg_client)
                await upload_file(s3_client, screenshot_filename)
                logging.info("скриншот успешно загружен в bucket")
            except (GotenbergServerError, httpx.HTTPError):
                logging.error(
                    "Скриншот не был сгенерирован, сайт отдается без него",
                    exc_info=True,
                )
            except (BotoCoreError, ClientError, FileNotFoundError):
                logging.error(
                    f"{screenshot_filename} файл не был загружен в bucket",
                    exc_info=True,
                )

    return StreamingResponse(
        stream_and_upload(),
        media_type="text/plain",
    )


@router.get(
    "/{site_id}",
    response_model=SiteResponse,
    summary="Получить сайт",
)
def get_site(site_id: int) -> SiteResponse:
    html_code_url = make_public_url("index.html")
    html_download_url = make_download_url(html_code_url, "index.html")
    screenshot_url = make_public_url("index.png")
    return SiteResponse(
        id=site_id,
        title="Фан клуб Домино",
        prompt="Сайт любителей играть в домино",
        html_code_url=html_code_url,
        html_code_download_url=html_download_url,
        screenshot_url=screenshot_url,
        created_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    )
