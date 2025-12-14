# SPDX-License-Identifier: MIT
import random, time
from typing import Callable, Type, Iterable, Any, Optional

class RetryError(Exception): ...

def retry(
    fn: Callable[[], Any],
    *,
    retries: int = 5,
    base: float = 0.25,
    cap: float = 5.0,
    jitter: float = 0.25,
    retry_on: Iterable[Type[BaseException]] = (Exception,),
) -> Any:
    """
    Exponential backoff with full jitter.
    base: initial sleep seconds, grows 2^n, capped at `cap`, plus [0, jitter) random.
    """
    attempt = 0
    while True:
        try:
            return fn()
        except retry_on as e:
            attempt += 1
            if attempt > retries:
                raise RetryError(f"Exceeded retry budget after {retries} attempts") from e
            sleep = min(cap, base * (2 ** (attempt - 1))) + random.random() * jitter
            time.sleep(sleep)
