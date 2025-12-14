"""
Async-safe utility functions for handling mixed sync/async callables.
Enables adapters to work with bus implementations that may be sync or async.
"""
from __future__ import annotations
import inspect
import asyncio
from typing import Any, Awaitable, Callable, Optional

async def maybe_await(value_or_coro: Any) -> Any:
    """Await value if it is awaitable, otherwise return it."""
    if inspect.isawaitable(value_or_coro):
        return await value_or_coro  # type: ignore[no-any-return]
    return value_or_coro

async def retry_async(fn: Callable[[], Awaitable[Any] | Any],
                      attempts: int = 5,
                      base_delay: float = 0.15) -> Any:
    """Retry sync/async fn with exp backoff. Stops on success."""
    last_exc: Optional[BaseException] = None
    for i in range(attempts):
        try:
            return await maybe_await(fn())
        except BaseException as e:  # noqa: BLE001
            last_exc = e
            await asyncio.sleep(base_delay * (2 ** i))
    if last_exc:
        raise last_exc
