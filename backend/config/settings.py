from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8"
    )

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:35b-a3b"
    ollama_embed_model: str = "nomic-embed-text"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl_price: int = 3600
    redis_ttl_financials: int = 86400
    redis_ttl_llm: int = 21600

    # SQLite
    sqlite_db_path: str = "./database/financial_analyzer.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # Default tickers
    default_tickers: List[str] = ["AAPL", "MSFT", "GOOGL", "JPM", "XOM"]

    # Weaviate ← 补上这个！
    weaviate_url: str = "http://localhost:8080"

settings = Settings()
