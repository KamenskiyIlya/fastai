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


class S3Settings(BaseSettings):
    access_key: SecretStr
    secret_key: SecretStr
    bucket_name: str
    bucket_url: str = "http://127.0.0.1:9000"
    region_name: str = "us-east-1"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    deepseek: DeepSeekSettings
    unsplash: UnsplashSettings
    s3: S3Settings
    debug: bool = False


settings = Settings()  # type: ignore
