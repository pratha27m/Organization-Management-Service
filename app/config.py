from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MASTER_DB: str = "master_db"
    JWT_SECRET: str = "please_change_this_secret_in_prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24  # 1 day

    class Config:
        env_file = ".env"

settings = Settings()
