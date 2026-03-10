import json
import logging

from langchain_redis import RedisSemanticCache
from langchain_core.globals import set_llm_cache
from langchain_ollama import OllamaEmbeddings

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self):
        self._redis_client = None
        self._semantic_cache = None
        self._init_redis()

    def _init_redis(self):
        try:
            import redis

            self._redis_client = redis.from_url(
                settings.redis_url, socket_connect_timeout=2
            )
            self._redis_client.ping()
            logger.info("Redis connected successfully")

            # L2: Semantic cache for LLM responses
            self._semantic_cache = RedisSemanticCache(
                redis_url=settings.redis_url,
                embeddings=OllamaEmbeddings(
                    model=settings.ollama_embed_model,
                    base_url=settings.ollama_base_url,
                ),
                distance_threshold=0.15,
                ttl=settings.redis_ttl_llm,
            )
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Cache disabled.")

    def enable_llm_cache(self):
        """Enable global LLM semantic cache (L2)."""
        if self._semantic_cache:
            set_llm_cache(self._semantic_cache)
            logger.info("LLM semantic cache enabled")

    def cache_raw_data(
        self, ticker: str, data_type: str, data: dict, ttl: int = None
    ):
        """Store yfinance raw data in Redis L1 cache."""
        if not self._redis_client:
            return
        try:
            key = f"yf:{ticker.upper()}:{data_type}"
            ttl = ttl or settings.redis_ttl_financials
            self._redis_client.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.warning(f"Cache write failed [{ticker}/{data_type}]: {e}")

    def get_raw_data(self, ticker: str, data_type: str) -> dict | None:
        """Retrieve yfinance raw data from Redis L1 cache."""
        if not self._redis_client:
            return None
        try:
            key = f"yf:{ticker.upper()}:{data_type}"
            data = self._redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Cache read failed [{ticker}/{data_type}]: {e}")
            return None

    def invalidate_ticker(self, ticker: str):
        """Clear all cached data for a ticker."""
        if not self._redis_client:
            return
        try:
            pattern = f"yf:{ticker.upper()}:*"
            keys = self._redis_client.keys(pattern)
            if keys:
                self._redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys for {ticker}")
        except Exception as e:
            logger.warning(f"Cache invalidation failed for {ticker}: {e}")


cache_manager = CacheManager()
