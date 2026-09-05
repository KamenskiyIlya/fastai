import logging
from datetime import datetime

import anyio
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse

from generator import html_generator, make_screenshot
from s3_utils import get_site_urls, upload_file
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
    html_code_url, html_download_url, screenshot_url = get_site_urls()
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
    html_code_url, html_download_url, screenshot_url = get_site_urls()
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
    site_id: int,
    body: SiteGenerationRequest,
):
    async def stream_and_upload():
        try:
            with anyio.CancelScope(shield=True):
                async for chunk in html_generator(body.prompt):
                    yield chunk
                try:
                    await upload_file("index.html")
                    logging.info("HTML файл успешно загружен в bucket")
                except Exception:
                    logging.error(
                        "HTML файл не был загружен в bucket",
                        exc_info=True,
                    )
                try:
                    await make_screenshot()
                    await upload_file("index.png")
                    logging.info("скриншот успешно загружен в bucket")
                except Exception:
                    logging.error(
                        "скриншот не был загружен в bucket",
                        exc_info=True,
                    )
        except anyio.get_cancelled_exc_class():
            raise

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
    html_code_url, html_download_url, screenshot_url = get_site_urls()
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
