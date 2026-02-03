"""
Async Utilities Module

Helper functions for async operations including parallel execution with timeout,
retry with exponential backoff, and rate limiting.
"""

import asyncio
import time
import logging
from typing import Any, Callable, List, Optional, TypeVar
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def gather_with_timeout(
    *coroutines,
    timeout: float = 1.0,
    return_exceptions: bool = True
) -> List[Any]:
    """
    Execute multiple coroutines in parallel with a timeout.
    
    Args:
        *coroutines: Coroutines to execute
        timeout: Maximum time to wait in seconds
        return_exceptions: If True, exceptions are returned as results
        
    Returns:
        List of results (or exceptions if return_exceptions=True)
        
    Example:
        >>> results = await gather_with_timeout(
        ...     fetch_price(ticker),
        ...     fetch_news(ticker),
        ...     timeout=0.5
        ... )
    """
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*coroutines, return_exceptions=return_exceptions),
            timeout=timeout
        )
        return results
    except asyncio.TimeoutError:
        logger.warning(f"gather_with_timeout exceeded {timeout}s")
        if return_exceptions:
            return [asyncio.TimeoutError()] * len(coroutines)
        raise


async def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    **kwargs
) -> Any:
    """
    Retry async function with exponential backoff.
    
    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        backoff_factor: Multiplier for delay on each retry
        **kwargs: Keyword arguments for func
        
    Returns:
        Result from successful function call
        
    Raises:
        Last exception if all retries fail
        
    Example:
        >>> result = await retry_with_backoff(
        ...     fetch_data,
        ...     url,
        ...     max_retries=3,
        ...     initial_delay=1.0
        ... )
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"Retry successful after {attempt} attempts")
            
            return result
        
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed")
    
    raise last_exception


def rate_limit(calls_per_second: float):
    """
    Decorator to rate limit async function calls.
    
    Args:
        calls_per_second: Maximum calls allowed per second
        
    Example:
        >>> @rate_limit(calls_per_second=10)
        ... async def fetch_data(url):
        ...     ...
    """
    min_interval = 1.0 / calls_per_second
    last_call_time = [0.0]  # Use list to allow modification in closure
    lock = asyncio.Lock()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with lock:
                # Calculate time to wait
                elapsed = time.time() - last_call_time[0]
                if elapsed < min_interval:
                    wait_time = min_interval - elapsed
                    await asyncio.sleep(wait_time)
                
                last_call_time[0] = time.time()
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


async def run_with_semaphore(
    coroutines: List,
    max_concurrent: int = 5
) -> List[Any]:
    """
    Run coroutines with limited concurrency.
    
    Args:
        coroutines: List of coroutines to execute
        max_concurrent: Maximum concurrent executions
        
    Returns:
        List of results
        
    Example:
        >>> tasks = [fetch_data(url) for url in urls]
        >>> results = await run_with_semaphore(tasks, max_concurrent=5)
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_task(coro):
        async with semaphore:
            return await coro
    
    return await asyncio.gather(*[bounded_task(coro) for coro in coroutines])


class AsyncTimer:
    """
    Context manager for timing async operations.
    
    Example:
        >>> async with AsyncTimer() as timer:
        ...     await some_operation()
        >>> print(f"Took {timer.elapsed_ms:.0f}ms")
    """
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds"""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        return self.elapsed_seconds * 1000
