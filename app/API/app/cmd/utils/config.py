from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # FastAPI metadata
    app_name: str = "SEA-SEC Demo"
    app_version: str = "0.1"
    app_env: str = "development"

    # API server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (optional, if you enable Postgres later)
    db_user: str = "seasec"
    db_password: str = "seasecpass"
    db_name: str = "seasec"
    db_host: str = "db"
    db_port: int = 5432

    # Security
    secret_key: str = "supersecretkey"

    class Config:
        env_file = ".env"  # load from .env file automatically
        env_file_encoding = "utf-8"

# Singleton settings instance
settings = Settings()

