from collections.abc import AsyncGenerator
from pathlib import Path

import anyio
import httpx
from fastapi import HTTPException
from html_page_generator import (
    AsyncPageGenerator,
)

from env_settings import settings

GENERATED_HTML_PATH = Path(__file__).resolve().parent.parent / "index.html"


async def html_generator(prompt: str) -> AsyncGenerator[str, None]:
    with anyio.CancelScope(shield=True):
        try:
            generator = AsyncPageGenerator(debug_mode=settings.debug)
            async for chunk in generator(prompt):
                print(chunk, end="", flush=True)
                yield chunk
            GENERATED_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
            GENERATED_HTML_PATH.write_text(
                generator.html_page.html_code,
                encoding="utf-8",
            )
            print("Генерация завершена полностью без ошибок")
        except anyio.get_cancelled_exc_class():
            raise
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=504,
                detail="Таймаут нейросети",
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Ошибка со стороны стороннего сервиса: "
                    f"{exc.response.status_code}"
                ),
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail="Сеть недоступна",
            ) from exc
