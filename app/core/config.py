from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    app_name: str = 'client-manager'
    database_url: str = 'sqlite:///./client_manager.db'
    log_level: str = 'INFO'

    pipefy_token: str = ''


settings: Settings = Settings()
