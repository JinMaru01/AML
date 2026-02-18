from src.core.redis import RedisClient
from src.core.redis_state import AccountStateStore

# Initialize singleton client
redis_client = RedisClient.get_client()

# Initialize account state store
store = AccountStateStore(redis_client)

# Save state for an account
account_id = "ACC12345"
state = {
    "risk_score": 0.87,
    "last_txn_time": "2026-02-18T08:15:00",
    "suspicious_txn_count": 3
}
store.save_state(account_id, state, expire_seconds=3600)

# Retrieve state
retrieved_state = store.get_state(account_id)
print(retrieved_state)

# Delete state
# store.delete_state(account_id)
