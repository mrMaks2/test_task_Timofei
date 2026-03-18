from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    BOT_INTERNAL_TOKEN: str
    ADMIN_CHAT_ID: int
    WEBAPP_URL: str = "http://localhost:5173"
    MEDIA_BASE_URL: str = "http://localhost:8000"
    LOG_LEVEL: str = "INFO"
    ADMIN_IDS: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def admin_ids(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]


settings = Settings()
