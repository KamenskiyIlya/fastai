import logging
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest
from html_page_generator import (
    AsyncPageGenerator,
)

from env_settings import settings

GENERATED_HTML_PATH = Path(__file__).resolve().parent.parent / "index.html"
SCREENSHOT_PATH = Path(__file__).resolve().parent.parent / "index.png"


async def html_generator(prompt: str) -> AsyncGenerator[str, None]:
    try:
        generator = AsyncPageGenerator(debug_mode=settings.debug)
        async for chunk in generator(prompt):
            if not isinstance(chunk, str):
                continue
            print(chunk, end="", flush=True)
            yield chunk
        GENERATED_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
        GENERATED_HTML_PATH.write_text(
            generator.html_page.html_code,
            encoding="utf-8",
        )
        logging.info("Генерация завершена полностью без ошибок")
    except httpx.TimeoutException as exc:
        logging.error(
            "Генерация прервана: таймаут нейросети",
            exc_info=exc,
        )
        raise
    except httpx.HTTPStatusError as exc:
        logging.error(
            "Генерация прервана: ошибка со стороны стороннего сервиса",
            exc_info=exc,
        )
        raise
    except httpx.HTTPError as exc:
        logging.error(
            "Генерация прервана: сеть недоступна",
            exc_info=exc,
        )
        raise
    except Exception as exc:
        logging.error("Генерация прервана: неожиданная ошибка", exc_info=exc)
        raise


async def make_screenshot() -> None:
    raw_html = GENERATED_HTML_PATH.read_text(encoding="utf-8")
    try:
        async with httpx.AsyncClient(
            base_url=settings.gotenberg.base_url,
            timeout=httpx.Timeout(
                settings.gotenberg.connect_timeout,
                read=settings.gotenberg.wait_delay + 5,
            ),
            limits=httpx.Limits(
                max_connections=settings.gotenberg.max_pool_connections,
            ),
        ) as client:
            screenshot_bytes = await ScreenshotHTMLRequest(
                index_html=raw_html,
                width=settings.gotenberg.screenshot_width,
                format=settings.gotenberg.screenshot_format,
                wait_delay=settings.gotenberg.wait_delay,
            ).asend(client)
        SCREENSHOT_PATH.write_bytes(screenshot_bytes)
        logging.info("Скриншот сайта успешно сгенерирован")
    except GotenbergServerError as exc:
        logging.error("Ошибка Gotenberg при генерации скриншота", exc_info=exc)
        raise
