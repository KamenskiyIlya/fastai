import logging
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
from html_page_generator import (
    AsyncPageGenerator,
)

from env_settings import settings

GENERATED_HTML_PATH = Path(__file__).resolve().parent.parent / "index.html"


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
