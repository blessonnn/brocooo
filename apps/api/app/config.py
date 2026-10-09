"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All config is loaded from environment / .env file."""

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "sqlite:///./brocooo.db"

    # Storage
    storage_dir: str = "./storage"

    # LLM providers (all optional — failover chain)
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # Media APIs
    pexels_api_key: str | None = None
    pixabay_api_key: str | None = None
    youtube_data_api_key: str | None = None

    # Transcription
    whisper_model: str = "small"
    groq_whisper_enabled: bool = False

    # TTS
    kokoro_model_path: str = "./models/kokoro-82m"
    piper_model_path: str = "./models/piper"

    # Fair-use limits
    max_concurrent_jobs_per_user: int = 3
    max_daily_jobs_per_ip: int = 50
    file_cleanup_days: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
