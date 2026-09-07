import logging
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
from gotenberg_api import ScreenshotHTMLRequest
from html_page_generator import (
    AsyncPageGenerator,
)

from env_settings import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_filename(site_id: int, filename: str) -> str:
    return f"{Path(filename).stem}_{site_id}{Path(filename).suffix}"


def delete_site_file(filename: str) -> None:
    (PROJECT_ROOT / filename).unlink(missing_ok=True)


async def html_generator(
    prompt: str,
    site_id: int,
) -> AsyncGenerator[str, None]:
    try:
        generator = AsyncPageGenerator(debug_mode=settings.debug)
        async for chunk in generator(prompt):
            if not isinstance(chunk, str):
                continue
            print(chunk, end="", flush=True)
            yield chunk
        html_path = PROJECT_ROOT / get_filename(site_id, "index.html")
        html_path.write_text(
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


async def make_screenshot(client: httpx.AsyncClient, site_id: int) -> None:
    html_path = PROJECT_ROOT / get_filename(site_id, "index.html")
    raw_html = html_path.read_text(encoding="utf-8")
    screenshot_bytes = await ScreenshotHTMLRequest(
        index_html=raw_html,
        width=settings.gotenberg.screenshot_width,
        format=settings.gotenberg.screenshot_format,
        wait_delay=settings.gotenberg.wait_delay,
    ).asend(client)
    screenshot_path = PROJECT_ROOT / get_filename(site_id, "index.png")
    screenshot_path.write_bytes(screenshot_bytes)
    logging.info("Скриншот сайта успешно сгенерирован")
