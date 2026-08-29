from pydantic import PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeepSeekSettings(BaseSettings):
    api_key: SecretStr
    base_url: str = ""
    model: str = ""
    max_connections: PositiveInt | None = None


class UnsplashSettings(BaseSettings):
    client_id: SecretStr
    max_connections: PositiveInt | None = None
    timeout: PositiveInt = 15


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    deepseek: DeepSeekSettings
    unsplash: UnsplashSettings
    debug: bool = False


settings = Settings()
