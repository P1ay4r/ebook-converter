import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    concurrent_workers: int = 4
    file_max_size: int = 209_715_200  # 200MB
    file_ttl_hours: int = 24
    storage_dir: str = "./storage"

    @property
    def upload_dir(self) -> str:
        return os.path.join(self.storage_dir, "uploads")

    @property
    def output_dir(self) -> str:
        return os.path.join(self.storage_dir, "output")

    @property
    def covers_dir(self) -> str:
        return os.path.join(self.storage_dir, "covers")

    @property
    def temp_dir(self) -> str:
        return os.path.join(self.storage_dir, "temp")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
