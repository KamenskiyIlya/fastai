import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, Field

app = FastAPI()


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
    prompt: str
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
                "htmlCodeUrl": "http://google.com/media/index.html",
                "htmlCodeDownloadUrl": "http://google.com/media/index.html?response-content-disposition=attachment",
                "screenshotUrl": "http://google.com/media/index.png",
                "createdAt": "2025-06-15T18:29:56+00:00",
                "updatedAt": "2025-06-15T18:29:56+00:00",
            },
        },
    )


class SiteGenerationRequest(BaseModel):
    prompt: str

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
                        "htmlCodeUrl": "http://127.0.0.1:8000/generated_index.html",
                        "htmlCodeDownloadUrl": "http://127.0.0.1:8000/generated_index.html",
                        "screenshotUrl": "https://google.com/media/index.png",
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
    site = SiteResponse(
        id=1,
        title="Фан клуб Домино",
        prompt="Сайт любителей играть в домино",
        htmlCodeUrl="http://127.0.0.1:8000/generated_index.html",
        htmlCodeDownloadUrl="http://127.0.0.1:8000/generated_index.html",
        screenshotUrl="https://google.com/media/index.png",
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
    return SiteResponse(
        id=1,
        title=body.title or "Фан клуб Домино",
        prompt=body.prompt,
        htmlCodeUrl="http://127.0.0.1:8000/generated_index.html",
        htmlCodeDownloadUrl="http://127.0.0.1:8000/generated_index.html",
        screenshotUrl="https://google.com/media/index.png",
        createdAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    )


@app.post(
    "/sites/{site_id}/generate",
    summary="Сгенерировать HTML разметку сайта",
    tags=["Sites"],
)
async def generate_site(
    site_id: int,
    body: SiteGenerationRequest | None = None,
):
    html_path = Path("frontend/generated_index.html")
    with html_path.open(encoding="utf-8") as html_file:
        html_content = html_file.read()

    chunk_size = 500

    async def html_chunk_generator():
        for chunk_start in range(0, len(html_content), chunk_size):
            html_chunk = html_content[chunk_start : chunk_start + chunk_size]
            yield html_chunk
            await asyncio.sleep(0.10)

    return StreamingResponse(html_chunk_generator(), media_type="text/html")


@app.get(
    "/sites/{site_id}",
    response_model=SiteResponse,
    summary="Получить сайт",
    tags=["Sites"],
)
def get_site(site_id: int) -> SiteResponse:
    return SiteResponse(
        id=site_id,
        title="Фан клуб Домино",
        prompt="Сайт любителей играть в домино",
        htmlCodeUrl="http://127.0.0.1:8000/generated_index.html",
        htmlCodeDownloadUrl="http://127.0.0.1:8000/generated_index.html",
        screenshotUrl="https://google.com/media/index.png",
        createdAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    )


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
