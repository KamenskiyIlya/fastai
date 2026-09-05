import logging
from contextlib import asynccontextmanager

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
    ):
        app.state.settings = settings
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(sites_router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
