from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    image_backend: str = "hf"

    hf_token: str = ""
    hf_image_model: str = "stabilityai/stable-diffusion-3.5-large"
    hf_provider: str = "auto"

    local_image_model: str = "runwayml/stable-diffusion-v1-5"

    max_prompt_length: int = 1200
    max_character_length: int = 60
    max_setting_length: int = 100

    static_dir: Path = BASE_DIR / "static"
    panels_dir: Path = BASE_DIR / "static" / "panels"
    exports_dir: Path = BASE_DIR / "static" / "exports"
    templates_dir: Path = BASE_DIR / "templates"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def ensure_directories(self) -> None:
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.panels_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings