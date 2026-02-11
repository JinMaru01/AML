from src.core.config import load_env_by_prefix
from src.core.database import Database
from src.core.redis import RedisClient

DBConnection = {}

class app:
    con = None
    redis = None
    envDict = load_env_by_prefix("MLAPP", [])

    @staticmethod
    def getDBCon():
        if app.con is None:
            app.con = Database()
            print("✅ Database connected successfully")
        return app.con.engine()
    
    @staticmethod
    def getRedis():
        if app.redis is None:
            app.redis = RedisClient()
            print("✅ Redis client initialized")
        return app.redis.get_client()