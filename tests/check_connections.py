"""
Test script to verify database and Redis connections.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import Database
from src.core.redis import RedisClient


def test_database_connection():
    """Test PostgreSQL database connection."""
    print("\n" + "="*50)
    print("Testing Database Connection")
    print("="*50)
    
    try:
        db = Database()
        engine = db.engine()
        
        # Test query
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            row = result.fetchone()
            print(f"✅ Database query successful: {row}")
        
        print("✅ Database connection test PASSED")
        return True
    except Exception as e:
        print(f"❌ Database connection test FAILED: {e}")
        return False


def test_redis_connection():
    """Test Redis connection."""
    print("\n" + "="*50)
    print("Testing Redis Connection")
    print("="*50)
    
    try:
        redis_client = RedisClient()
        client = redis_client.get_client()
        
        # Test basic operations
        client.set("test_key", "test_value")
        value = client.get("test_key")
        print(f"✅ Redis SET/GET successful: {value}")
        
        # Cleanup
        client.delete("test_key")
        
        print("✅ Redis connection test PASSED")
        return True
    except Exception as e:
        print(f"❌ Redis connection test FAILED: {e}")
        print(f"   Make sure Redis is running and REDIS_* env vars are set")
        return False


def main():
    """Run all connection tests."""
    print("\n" + "="*60)
    print("CONNECTION TESTS")
    print("="*60)
    
    db_passed = test_database_connection()
    redis_passed = test_redis_connection()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Database: {'✅ PASSED' if db_passed else '❌ FAILED'}")
    print(f"Redis:    {'✅ PASSED' if redis_passed else '❌ FAILED'}")
    print("="*60 + "\n")
    
    return db_passed and redis_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
