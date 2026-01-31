from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Set

class Settings(BaseSettings):
    # Logging
    LOG_LEVEL: str
    LOG_FORMAT: str
    
    # Bot
    BOT_TOKEN: str
    BOT_ADMIN_IDS_STR: str
    
    # Database
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    
    # Redis    
    REDIS_DB_NUM: int
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str
    REDIS_PASSWORD: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    
    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def DATABASE_URL_SYNC(self):
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        
    @property
    def BOT_ADMIN_IDS(self) -> Set[int]:
        if not self.BOT_ADMIN_IDS_STR.strip():
            return set()
        return {int(x.strip()) for x in self.BOT_ADMIN_IDS_STR.split(",") if x.strip()}
    
settings = Settings()