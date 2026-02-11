from typing import Optional
import redis
from redis import Redis
from src.core.config import load_env_by_prefix


class RedisClient:
    """Singleton Redis client for the application."""
    
    _client: Optional[Redis] = None
    _config: Optional[dict] = None

    def __init__(self, decode_responses: bool = True):
        """Initialize Redis client if not already initialized."""
        if RedisClient._client is None:
            RedisClient._config = self._load_config()
            RedisClient._client = self._create_client(decode_responses)
            self._test_connection()

    def _load_config(self) -> dict:
        """Load Redis configuration from environment variables."""
        cfg = load_env_by_prefix("REDIS", [])
        return {
            "host": cfg.get("host", "localhost"),
            "port": cfg.get("port", 6379),
            "db": cfg.get("db", 0),
            "password": cfg.get("password", None),
            "socket_timeout": cfg.get("socket_timeout", 5),
            "socket_connect_timeout": cfg.get("socket_connect_timeout", 5),
            "max_connections": cfg.get("max_connections", 50),
        }

    def _create_client(self, decode_responses: bool) -> Redis:
        """Create Redis client with connection pooling."""
        c = RedisClient._config
        
        connection_pool = redis.ConnectionPool(
            host=c["host"],
            port=c["port"],
            db=c["db"],
            password=c["password"],
            socket_timeout=c["socket_timeout"],
            socket_connect_timeout=c["socket_connect_timeout"],
            max_connections=c["max_connections"],
            decode_responses=decode_responses,
        )
        
        return Redis(connection_pool=connection_pool)

    def _test_connection(self):
        """Test Redis connection."""
        try:
            RedisClient._client.ping()
            print(f"✅ Redis connected successfully to {RedisClient._config['host']}:{RedisClient._config['port']}")
        except redis.ConnectionError as e:
            print(f"❌ Redis connection failed: {e}")
            raise

    @classmethod
    def get_client(cls) -> Redis:
        """Get the Redis client instance."""
        if cls._client is None:
            cls()
        return cls._client

    @classmethod
    def close(cls):
        """Close the Redis connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            print("Redis connection closed")
