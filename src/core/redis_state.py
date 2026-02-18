import json
from typing import Any, Dict
from .redis import RedisClient

class AccountStateStore:
    """Store and retrieve account state in Redis."""

    PREFIX = "account_state:"  # Redis key prefix

    def __init__(self, redis_client: None):
        self.redis = redis_client

    def _key(self, account_id: str) -> str:
        """Generate Redis key for the account."""
        return f"{self.PREFIX}{account_id}"

    def save_state(self, account_id: str, state: Dict[str, Any], expire_seconds: int = 3600):
        """
        Save the account state to Redis.

        Args:
            account_id: Unique account identifier
            state: Dictionary of account state (e.g., ML features, risk score)
            expire_seconds: TTL for the key (default 1 hour)
        """
        key = self._key(account_id)
        # Store as JSON string
        self.redis.set(key, json.dumps(state), ex=expire_seconds)

    def get_state(self, account_id: str) -> Dict[str, Any]:
        """
        Retrieve account state from Redis.

        Returns:
            Dictionary of state, or empty dict if not found
        """
        key = self._key(account_id)
        raw = self.redis.get(key)
        if raw is None:
            return {}
        return json.loads(raw)

    def delete_state(self, account_id: str):
        """Remove account state from Redis."""
        key = self._key(account_id)
        self.redis.delete(key)
