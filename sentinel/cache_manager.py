"""
Cache Manager Module

Multi-tier caching system with in-memory L1 and persistent L2 (SQLite) storage.
Solves the latency chain of death by providing <10ms cached lookups.

Architecture:
- L1 Cache: In-memory LRU (max 1000 items, <1ms access)
- L2 Cache: SQLite persistent storage (<10ms access)
- Automatic tier promotion/demotion
- TTL-based expiration
"""

import asyncio
import json
import time
import logging
from collections import OrderedDict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, Optional, List
from pathlib import Path

try:
    import aiosqlite
except ImportError:
    aiosqlite = None

logger = logging.getLogger(__name__)


class CacheTier(Enum):
    """Cache tier levels"""
    MEMORY = auto()   # L1: In-memory LRU cache
    DISK = auto()     # L2: SQLite persistent cache
    NETWORK = auto()  # L3: Remote/API call (cache miss)


@dataclass
class CachedData:
    """
    Cached data entry with metadata.
    
    Attributes:
        key: Cache key (e.g., "supply_chain:AAPL")
        value: Cached value (JSON-serializable)
        created_at: Timestamp when cached
        ttl_seconds: Time-to-live in seconds
        access_count: Number of times accessed
        last_accessed: Last access timestamp
    """
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int = 86400  # 24 hours default
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        age = time.time() - self.created_at
        return age > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds"""
        return time.time() - self.created_at
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CachedData':
        """Create from dictionary"""
        return cls(**data)


class LRUCache:
    """
    Simple LRU (Least Recently Used) cache implementation.
    
    Thread-safe in-memory cache with automatic eviction of least recently used items.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items to store
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, CachedData] = OrderedDict()
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[CachedData]:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            CachedData if found and not expired, None otherwise
        """
        async with self._lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired:
                del self.cache[key]
                logger.debug(f"L1 cache expired: {key}")
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            
            # Update access metadata
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            logger.debug(f"L1 cache hit: {key} (age={entry.age_seconds:.1f}s)")
            return entry
    
    async def set(self, key: str, entry: CachedData) -> None:
        """
        Set item in cache.
        
        Args:
            key: Cache key
            entry: CachedData to store
        """
        async with self._lock:
            # Remove if exists (to update position)
            if key in self.cache:
                del self.cache[key]
            
            # Add to end (most recently used)
            self.cache[key] = entry
            
            # Evict oldest if over capacity
            if len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                logger.debug(f"L1 cache evicted: {oldest_key}")
            
            logger.debug(f"L1 cache set: {key}")
    
    async def delete(self, key: str) -> bool:
        """Delete item from cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
            logger.info("L1 cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size if self.max_size > 0 else 0
        }


class CacheManager:
    """
    Multi-tier cache manager with L1 (memory) and L2 (SQLite) storage.
    
    Provides fast cached lookups with automatic tier promotion and TTL expiration.
    
    Example:
        >>> cache = CacheManager(db_path="./sentinel_state/cache.db")
        >>> await cache.initialize()
        >>> await cache.set("supply_chain:AAPL", {"suppliers": ["TSMC"]}, ttl=86400)
        >>> data = await cache.get("supply_chain:AAPL")
    """
    
    def __init__(
        self,
        db_path: str = "./sentinel_state/cache.db",
        l1_max_size: int = 1000,
        enable_l2: bool = True
    ):
        """
        Initialize cache manager.
        
        Args:
            db_path: Path to SQLite database for L2 cache
            l1_max_size: Maximum items in L1 cache
            enable_l2: Whether to enable L2 disk cache
        """
        self.db_path = Path(db_path)
        self.l1_max_size = l1_max_size
        self.enable_l2 = enable_l2 and aiosqlite is not None
        
        # L1 cache (memory)
        self.l1_cache = LRUCache(max_size=l1_max_size)
        
        # L2 cache (SQLite)
        self.db_conn: Optional[aiosqlite.Connection] = None
        
        # Metrics
        self.metrics = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "sets": 0
        }
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize cache manager and create database schema"""
        if self._initialized:
            return
        
        # Create state directory
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize L2 cache if enabled
        if self.enable_l2:
            self.db_conn = await aiosqlite.connect(str(self.db_path))
            
            # Create cache table
            await self.db_conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    ttl_seconds INTEGER NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL NOT NULL
                )
            """)
            
            # Create index on created_at for cleanup
            await self.db_conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON cache(created_at)
            """)
            
            await self.db_conn.commit()
            logger.info(f"L2 cache initialized: {self.db_path}")
        
        self._initialized = True
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (checks L1 then L2).
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        if not self._initialized:
            await self.initialize()
        
        # Try L1 cache first
        entry = await self.l1_cache.get(key)
        if entry is not None:
            self.metrics["l1_hits"] += 1
            return entry.value
        
        # Try L2 cache
        if self.enable_l2 and self.db_conn:
            entry = await self._get_from_l2(key)
            if entry is not None:
                self.metrics["l2_hits"] += 1
                
                # Promote to L1
                await self.l1_cache.set(key, entry)
                
                return entry.value
        
        # Cache miss
        self.metrics["misses"] += 1
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 86400
    ) -> None:
        """
        Set value in cache (both L1 and L2).
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time-to-live in seconds (default 24 hours)
        """
        if not self._initialized:
            await self.initialize()
        
        entry = CachedData(
            key=key,
            value=value,
            ttl_seconds=ttl
        )
        
        # Set in L1
        await self.l1_cache.set(key, entry)
        
        # Set in L2
        if self.enable_l2 and self.db_conn:
            await self._set_in_l2(entry)
        
        self.metrics["sets"] += 1
        logger.debug(f"Cache set: {key} (ttl={ttl}s)")
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from all cache tiers.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was found and deleted
        """
        if not self._initialized:
            await self.initialize()
        
        deleted = False
        
        # Delete from L1
        if await self.l1_cache.delete(key):
            deleted = True
        
        # Delete from L2
        if self.enable_l2 and self.db_conn:
            cursor = await self.db_conn.execute(
                "DELETE FROM cache WHERE key = ?",
                (key,)
            )
            await self.db_conn.commit()
            if cursor.rowcount > 0:
                deleted = True
        
        return deleted
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        if not self._initialized:
            await self.initialize()
        
        await self.l1_cache.clear()
        
        if self.enable_l2 and self.db_conn:
            await self.db_conn.execute("DELETE FROM cache")
            await self.db_conn.commit()
        
        logger.info("All caches cleared")
    
    async def cleanup_expired(self) -> int:
        """
        Remove expired entries from L2 cache.
        
        Returns:
            Number of entries removed
        """
        if not self.enable_l2 or not self.db_conn:
            return 0
        
        current_time = time.time()
        
        cursor = await self.db_conn.execute("""
            DELETE FROM cache 
            WHERE (created_at + ttl_seconds) < ?
        """, (current_time,))
        
        await self.db_conn.commit()
        
        removed = cursor.rowcount
        if removed > 0:
            logger.info(f"Cleaned up {removed} expired cache entries")
        
        return removed
    
    async def warm_cache(self, keys: List[str], fetcher_func) -> int:
        """
        Warm cache by pre-fetching data for given keys.
        
        Args:
            keys: List of cache keys to warm
            fetcher_func: Async function to fetch data for a key
            
        Returns:
            Number of keys successfully warmed
        """
        warmed = 0
        
        for key in keys:
            try:
                # Check if already cached
                existing = await self.get(key)
                if existing is not None:
                    continue
                
                # Fetch and cache
                value = await fetcher_func(key)
                if value is not None:
                    await self.set(key, value)
                    warmed += 1
            except Exception as e:
                logger.error(f"Failed to warm cache for {key}: {e}")
        
        logger.info(f"Cache warmed: {warmed}/{len(keys)} keys")
        return warmed
    
    async def _get_from_l2(self, key: str) -> Optional[CachedData]:
        """Get entry from L2 cache"""
        if not self.db_conn:
            return None
        
        cursor = await self.db_conn.execute(
            "SELECT value, created_at, ttl_seconds, access_count, last_accessed FROM cache WHERE key = ?",
            (key,)
        )
        
        row = await cursor.fetchone()
        if row is None:
            return None
        
        value_json, created_at, ttl_seconds, access_count, last_accessed = row
        
        entry = CachedData(
            key=key,
            value=json.loads(value_json),
            created_at=created_at,
            ttl_seconds=ttl_seconds,
            access_count=access_count,
            last_accessed=last_accessed
        )
        
        # Check expiration
        if entry.is_expired:
            await self.db_conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            await self.db_conn.commit()
            logger.debug(f"L2 cache expired: {key}")
            return None
        
        # Update access metadata
        entry.access_count += 1
        entry.last_accessed = time.time()
        
        await self.db_conn.execute(
            "UPDATE cache SET access_count = ?, last_accessed = ? WHERE key = ?",
            (entry.access_count, entry.last_accessed, key)
        )
        await self.db_conn.commit()
        
        logger.debug(f"L2 cache hit: {key} (age={entry.age_seconds:.1f}s)")
        return entry
    
    async def _set_in_l2(self, entry: CachedData) -> None:
        """Set entry in L2 cache"""
        if not self.db_conn:
            return
        
        await self.db_conn.execute("""
            INSERT OR REPLACE INTO cache (key, value, created_at, ttl_seconds, access_count, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry.key,
            json.dumps(entry.value),
            entry.created_at,
            entry.ttl_seconds,
            entry.access_count,
            entry.last_accessed
        ))
        
        await self.db_conn.commit()
    
    def get_metrics(self) -> Dict:
        """Get cache performance metrics"""
        total_requests = self.metrics["l1_hits"] + self.metrics["l2_hits"] + self.metrics["misses"]
        
        return {
            **self.metrics,
            "total_requests": total_requests,
            "hit_rate": (self.metrics["l1_hits"] + self.metrics["l2_hits"]) / max(total_requests, 1),
            "l1_stats": self.l1_cache.get_stats()
        }
    
    async def close(self) -> None:
        """Close database connection"""
        if self.db_conn:
            await self.db_conn.close()
            logger.info("Cache manager closed")
