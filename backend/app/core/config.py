from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/callback"
    secret_key: str
    frontend_url: str = "http://localhost:5173"
    sync_interval_hours: int = 6
    detection_threshold: int = 50

    class Config:
        env_file = ".env"


settings = Settings()
