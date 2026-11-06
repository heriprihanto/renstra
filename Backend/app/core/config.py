from typing import List, Union
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "RENSTRA KOTA TEGAL"
    ENVIRONMENT: str = "local"
    TAHUN_ANGGARAN: int = 2026

    # Postgresql credentials
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "db_renstra"

    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = "http://localhost,http://localhost:5173,http://localhost:8080"

    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, list):
            return self.BACKEND_CORS_ORIGINS
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            # Split comma separated origins
            return [orig.strip() for orig in self.BACKEND_CORS_ORIGINS.split(",") if orig.strip()]
        return ["*"]

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
