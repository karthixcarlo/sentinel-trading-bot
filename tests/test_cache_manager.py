"""
Unit tests for CacheManager module

Tests L1/L2 cache functionality, TTL expiration, and cache warming.
"""

import pytest
import asyncio
import time
from pathlib import Path
from sentinel.cache_manager import CacheManager, CachedData, CacheTier


@pytest.fixture
async def cache_manager():
    """Create cache manager for testing"""
    cache = CacheManager(
        db_path=":memory:",  # Use in-memory SQLite for testing
        l1_max_size=10
    )
    await cache.initialize()
    yield cache
    await cache.close()


@pytest.mark.asyncio
async def test_cache_initialization(cache_manager):
    """Test cache manager initialization"""
    assert cache_manager._initialized
    assert cache_manager.l1_cache is not None


@pytest.mark.asyncio
async def test_l1_cache_set_get(cache_manager):
    """Test L1 cache set and get"""
    await cache_manager.set("test_key", {"value": 123}, ttl=60)
    
    result = await cache_manager.get("test_key")
    
    assert result is not None
    assert result["value"] == 123
    assert cache_manager.metrics["l1_hits"] == 1


@pytest.mark.asyncio
async def test_l2_cache_promotion(cache_manager):
    """Test L2 to L1 cache promotion"""
    # Set in cache
    await cache_manager.set("test_key", {"value": 456}, ttl=60)
    
    # Clear L1 to force L2 lookup
    await cache_manager.l1_cache.clear()
    
    # Get should hit L2 and promote to L1
    result = await cache_manager.get("test_key")
    
    assert result is not None
    assert result["value"] == 456
    assert cache_manager.metrics["l2_hits"] == 1


@pytest.mark.asyncio
async def test_cache_miss(cache_manager):
    """Test cache miss"""
    result = await cache_manager.get("nonexistent_key")
    
    assert result is None
    assert cache_manager.metrics["misses"] == 1


@pytest.mark.asyncio
async def test_ttl_expiration(cache_manager):
    """Test TTL expiration"""
    # Set with 1 second TTL
    await cache_manager.set("short_ttl", {"value": 789}, ttl=1)
    
    # Should exist immediately
    result = await cache_manager.get("short_ttl")
    assert result is not None
    
    # Wait for expiration
    await asyncio.sleep(1.1)
    
    # Should be expired
    result = await cache_manager.get("short_ttl")
    assert result is None


@pytest.mark.asyncio
async def test_cache_delete(cache_manager):
    """Test cache deletion"""
    await cache_manager.set("delete_me", {"value": 999}, ttl=60)
    
    # Verify exists
    result = await cache_manager.get("delete_me")
    assert result is not None
    
    # Delete
    deleted = await cache_manager.delete("delete_me")
    assert deleted is True
    
    # Verify deleted
    result = await cache_manager.get("delete_me")
    assert result is None


@pytest.mark.asyncio
async def test_cache_clear(cache_manager):
    """Test clearing all cache"""
    # Add multiple entries
    for i in range(5):
        await cache_manager.set(f"key_{i}", {"value": i}, ttl=60)
    
    # Clear all
    await cache_manager.clear()
    
    # Verify all cleared
    for i in range(5):
        result = await cache_manager.get(f"key_{i}")
        assert result is None


@pytest.mark.asyncio
async def test_l1_lru_eviction(cache_manager):
    """Test L1 LRU eviction"""
    # Fill L1 cache beyond capacity (max_size=10)
    for i in range(15):
        await cache_manager.set(f"key_{i}", {"value": i}, ttl=60)
    
    # L1 should only have 10 items (most recent)
    l1_stats = cache_manager.l1_cache.get_stats()
    assert l1_stats["size"] <= 10


@pytest.mark.asyncio
async def test_cache_metrics(cache_manager):
    """Test cache metrics"""
    # Generate some cache activity
    await cache_manager.set("key1", {"value": 1}, ttl=60)
    await cache_manager.get("key1")  # L1 hit
    await cache_manager.get("nonexistent")  # Miss
    
    metrics = cache_manager.get_metrics()
    
    assert metrics["l1_hits"] >= 1
    assert metrics["misses"] >= 1
    assert metrics["sets"] >= 1
    assert "hit_rate" in metrics


@pytest.mark.asyncio
async def test_cache_warming():
    """Test cache warming functionality"""
    cache = CacheManager(db_path=":memory:")
    await cache.initialize()
    
    # Mock fetcher function
    async def mock_fetcher(key: str):
        return {"key": key, "data": f"fetched_{key}"}
    
    # Warm cache
    keys = ["ticker1", "ticker2", "ticker3"]
    warmed = await cache.warm_cache(keys, mock_fetcher)
    
    assert warmed == 3
    
    # Verify all keys cached
    for key in keys:
        result = await cache.get(key)
        assert result is not None
        assert result["key"] == key
    
    await cache.close()


@pytest.mark.asyncio
async def test_cached_data_expiration():
    """Test CachedData expiration logic"""
    # Create entry with 1 second TTL
    entry = CachedData(
        key="test",
        value={"data": 123},
        ttl_seconds=1
    )
    
    # Should not be expired immediately
    assert not entry.is_expired
    
    # Wait for expiration
    await asyncio.sleep(1.1)
    
    # Should be expired
    assert entry.is_expired


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
