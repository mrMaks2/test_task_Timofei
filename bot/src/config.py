from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    BOT_INTERNAL_TOKEN: str
    ADMIN_CHAT_ID: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()