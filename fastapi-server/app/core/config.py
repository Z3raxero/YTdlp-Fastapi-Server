from pydantic import BaseSettings

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Video Audio Extractor"
    api_version: str = "v1"
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    # Storage settings
    temporary_storage_path: str = "./temp"
    audio_storage_duration: int = 24  # in hours

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()