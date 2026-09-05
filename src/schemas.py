from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints


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
