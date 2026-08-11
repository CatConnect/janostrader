from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    ENCRYPTION_KEY: str
    ACCESS_KEY: str = "changeme"
    INTERNAL_KEY: str = "changeme-internal"
    STRATEGIES_VOLUME_PATH: str = "/strategies"
    STRATEGIES_SEED_PATH: str = "/app/strategies"   # dentro do container do hub

    class Config:
        env_file = ".env"


settings = Settings()

