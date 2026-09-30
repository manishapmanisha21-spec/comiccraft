import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routes import router


logging.basicConfig(level=logging.INFO)

settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    description="AI comic story creator using Gemini and AI image generation.",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=str(settings.static_dir)),
    name="static",
)


app.include_router(router)


@app.on_event("startup")
async def startup() -> None:
    settings.ensure_directories()