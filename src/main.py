import logging
from contextlib import asynccontextmanager

import aioboto3
from aiobotocore.config import AioConfig
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from html_page_generator import (
    AsyncDeepseekClient,
    AsyncUnsplashClient,
)

from env_settings import settings
from routes.sites import router as sites_router
from routes.users import router as users_router

logging.basicConfig(
    level=logging.INFO,
)

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with (
        AsyncUnsplashClient.setup(
            settings.unsplash.client_id.get_secret_value(),
            timeout=settings.unsplash.timeout,
        ),
        AsyncDeepseekClient.setup(
            settings.deepseek.api_key.get_secret_value(),
            str(settings.deepseek.base_url),
            settings.deepseek.model,
        ),
        _s3_session.client(  # type: ignore
            "s3",
            endpoint_url=str(settings.s3.bucket_url),
            config=_s3_config,
        ) as s3_client,
    ):
        app.state.settings = settings
        app.state.s3_client = s3_client
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(sites_router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
