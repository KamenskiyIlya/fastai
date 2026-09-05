import logging
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
from gotenberg_api import ScreenshotHTMLRequest
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
    except httpx.TimeoutException:
        logging.error(
            "Генерация прервана: таймаут нейросети",
            exc_info=True,
        )
        raise
    except httpx.HTTPStatusError:
        logging.error(
            "Генерация прервана: ошибка со стороны стороннего сервиса",
            exc_info=True,
        )
        raise
    except httpx.HTTPError:
        logging.error(
            "Генерация прервана: сеть недоступна",
            exc_info=True,
        )
        raise


async def make_screenshot(client: httpx.AsyncClient) -> None:
    raw_html = GENERATED_HTML_PATH.read_text(encoding="utf-8")
    screenshot_bytes = await ScreenshotHTMLRequest(
        index_html=raw_html,
        width=settings.gotenberg.screenshot_width,
        format=settings.gotenberg.screenshot_format,
        wait_delay=settings.gotenberg.wait_delay,
    ).asend(client)
    SCREENSHOT_PATH.write_bytes(screenshot_bytes)
    logging.info("Скриншот сайта успешно сгенерирован")
