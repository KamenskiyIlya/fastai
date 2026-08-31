import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

import anyio
from fastapi import FastAPI, HTTPException
from fastapi.responses import (
    FileResponse,
    PlainTextResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from html_page_generator import (
    AsyncDeepseekClient,
    AsyncUnsplashClient,
)
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from env_settings import settings
from generator import GENERATED_HTML_PATH, html_generator
from s3_utils import get_site_urls, upload_file

logging.basicConfig(
    level=logging.INFO,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with (
        AsyncUnsplashClient.setup(
            settings.unsplash.client_id.get_secret_value(),
            timeout=settings.unsplash.timeout,
        ),
        AsyncDeepseekClient.setup(
            settings.deepseek.api_key.get_secret_value(),
            settings.deepseek.base_url,
            settings.deepseek.model,
        ),
    ):
        app.state.settings = settings
        yield


app = FastAPI(lifespan=lifespan)

print(settings.model_dump_json(indent=2))


class UserDetailsResponse(BaseModel):
    profileId: int
    email: EmailStr
    username: str = Field(..., max_length=254)
    registeredAt: datetime
    updatedAt: datetime
    isActive: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "example@example.com",
                "isActive": True,
                "profileId": "1",
                "registeredAt": "2025-06-15T18:29:56+00:00",
                "updatedAt": "2025-06-15T18:29:56+00:00",
                "username": "user123",
            },
        },
    )


class CreateSiteRequest(BaseModel):
    prompt: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=5,
            max_length=4000,
        ),
    ]
    title: str | None = Field(default=None, max_length=128)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Сайт любителей играть в домино",
                "title": "Фан клуб игры в домино",
            },
        },
    )


class SiteResponse(BaseModel):
    id: int
    title: str
    prompt: str
    htmlCodeUrl: str | None
    htmlCodeDownloadUrl: str | None
    screenshotUrl: str | None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Фан клуб Домино",
                "prompt": "Сайт любителей играть в домино",
                "htmlCodeUrl": "http://127.0.0.1:9000/fastai-html/index.html",
                "htmlCodeDownloadUrl": "http://127.0.0.1:9000/fastai-"
                "html/index.html?response-content-disposition=attachme"
                "nt%3B+filename%3D%22index.html%22",
                "screenshotUrl": "http://127.0.0.1:9000/fastai-html/index.png",
                "createdAt": "2025-06-15T18:29:56+00:00",
                "updatedAt": "2025-06-15T18:29:56+00:00",
            },
        },
    )


class SiteGenerationRequest(BaseModel):
    prompt: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=5,
            max_length=4000,
        ),
    ]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"prompt": "Сайт любителей играть в домино"},
        },
    )


class GeneratedSitesResponse(BaseModel):
    sites: list[SiteResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sites": [
                    {
                        "id": 1,
                        "title": "Фан клуб Домино",
                        "prompt": "Сайт любителей играть в домино",
                        "htmlCodeUrl": "http://127.0.0.1:9000/fastai-html/index.html",
                        "htmlCodeDownloadUrl": "http://127.0.0.1:9000/fastai-"
                        "html/index.html?response-content-disposition=attachme"
                        "nt%3B+filename%3D%22index.html%22",
                        "screenshotUrl": "http://127.0.0.1:9000/fastai-html/index.png",
                        "createdAt": "2025-06-15T18:29:56+00:00",
                        "updatedAt": "2025-06-15T18:29:56+00:00",
                    },
                ],
            },
        },
    )


@app.get(
    "/users/me",
    response_model=UserDetailsResponse,
    summary="Получить учетные данные пользователя",
    response_description="Данные пользователя",
    tags=["Users"],
)
def get_user() -> UserDetailsResponse:
    return UserDetailsResponse(
        email="example@example.com",
        isActive=True,
        profileId=1,
        registeredAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        username="klol1k",
    )


@app.get(
    "/sites/my",
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
        htmlCodeUrl=html_code_url,
        htmlCodeDownloadUrl=html_download_url,
        screenshotUrl=screenshot_url,
        createdAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    )
    return GeneratedSitesResponse(sites=[site])


@app.post(
    "/sites/create",
    response_model=SiteResponse,
    summary="Создать сайт",
    tags=["Sites"],
)
def create_site(body: CreateSiteRequest) -> SiteResponse:
    html_code_url, html_download_url, screenshot_url = get_site_urls()
    return SiteResponse(
        id=1,
        title=body.title or "Фан клуб Домино",
        prompt=body.prompt,
        htmlCodeUrl=html_code_url,
        htmlCodeDownloadUrl=html_download_url,
        screenshotUrl=screenshot_url,
        createdAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    )


@app.post(
    "/sites/{site_id}/generate",
    summary="Сгенерировать HTML разметку сайта",
    description="Код сайта будет транслироваться стримом по мере генерации.",
    tags=["Sites"],
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
                    logging.info(
                        "HTML файл не был загружен в bucket",
                        exc_info=True,
                    )
        except anyio.get_cancelled_exc_class():
            raise

    return StreamingResponse(
        stream_and_upload(),
        media_type="text/plain",
    )


@app.get(
    "/sites/{site_id}",
    response_model=SiteResponse,
    summary="Получить сайт",
    tags=["Sites"],
)
def get_site(site_id: int) -> SiteResponse:
    html_code_url, html_download_url, screenshot_url = get_site_urls()
    return SiteResponse(
        id=site_id,
        title="Фан клуб Домино",
        prompt="Сайт любителей играть в домино",
        htmlCodeUrl=html_code_url,
        htmlCodeDownloadUrl=html_download_url,
        screenshotUrl=screenshot_url,
        createdAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    )


@app.get("/index.html", include_in_schema=False)
def provide_index():
    if not GENERATED_HTML_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="index.html was not generated",
        )
    return FileResponse(GENERATED_HTML_PATH, media_type="text/html")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
