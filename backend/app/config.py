from typing import Literal

from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class LoggingConfig(BaseModel):
    log_level: Literal[
        'debug',
        'info',
        'warning',
        'error',
        'critical',
    ] = 'info'
    log_format: str = LOG_DEFAULT_FORMAT


class GunicornConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    timeout: int = 900


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    ws: str = '/ws'
    users: str = "/users"
    chats: str = '/chats'
    assistants: str = '/assistants'


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class OpenAiConfig(BaseSettings):
    secret_hash_key: str = 'SECRET_HASH_KEY'
    api_key: str = 'api_key'
    bakai_automate_id: str = 'BAKAI_AUTOMATE_ID'
    bakai_hr_id: str = 'BAKAI_HR_ID'
    bakai_finance_id: str = 'BAKAI_FINANCE_ID'
    bakai_legal_id: str = 'BAKAI_LEGAL_ID'
    bakai_marketer_id: str = 'BAKAI_MARKETER_ID'
    bakai_tax_id: str = 'BAKAI_TAX_ID'
    bakai_accountant_id: str = 'BAKAI_ACCOUNTANT_ID'



class DatabaseConfig(BaseModel):
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'postgres'
    POSTGRES_HOST: str = 'database'  # Добавьте это поле
    POSTGRES_PORT: int = 5432
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self):
        template = "postgresql://{user}:{password}@database/{database}"
        return template.format(
            user=settings.db.POSTGRES_USER,
            password=settings.db.POSTGRES_PASSWORD,
            database=settings.db.POSTGRES_DB,
        )

    @property
    def async_url(self):
        template = "postgresql+asyncpg://{user}:{password}@database/{database}".format(
            user=settings.db.POSTGRES_USER,
            password=settings.db.POSTGRES_PASSWORD,
            host=settings.db.POSTGRES_HOST,
            database=settings.db.POSTGRES_DB,
        )
        return template


class RedisConfig(BaseModel):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env.dev", '.env.prod'),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    gunicorn: GunicornConfig = GunicornConfig()
    logging: LoggingConfig = LoggingConfig()
    api: ApiPrefix = ApiPrefix()
    redis: RedisConfig = RedisConfig()
    openai: OpenAiConfig = OpenAiConfig()
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()
