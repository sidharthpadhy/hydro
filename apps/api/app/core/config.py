from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Hydro Flood API"
    env: str = "dev"
    database_url: str = "sqlite:///./hydro.db"
    redis_url: str = "redis://localhost:6379/0"
    storage_root: str = "/tmp/hydro/storage"
    workspace_root: str = "/tmp/hydro/workspaces"
    max_upload_mb: int = 100
    use_mock_ras: bool = True


settings = Settings()
