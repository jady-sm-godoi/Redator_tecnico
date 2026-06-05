import time
import random
from functools import wraps
from typing import Callable, TypeVar, Any
from datetime import datetime, timezone

F = TypeVar("F", bound=Callable[..., Any])

RATE_LIMIT_WARN_THRESHOLD = 0.1  # warn when <10% remaining


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable[[F], F]:
    """Retry decorator with exponential backoff for transient API failures."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc = None
            attempt_delay = delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        jitter = random.uniform(0, 0.5 * attempt_delay)
                        time.sleep(attempt_delay + jitter)
                        attempt_delay *= backoff
            raise last_exc  # type: ignore
        return wrapper  # type: ignore
    return decorator


def _to_int(val: Any) -> int:
    """Safely convert a value to int, returning -1 on failure."""
    try:
        return int(val)
    except (TypeError, ValueError):
        return -1


def check_github_rate_limit(api: Any) -> tuple[int, int, datetime]:
    """Check GitHub API rate limit. Returns (remaining, limit, reset_time)."""
    try:
        rate = api.get_rate_limit().core
        remaining = _to_int(rate.remaining)
        limit = _to_int(rate.limit)
        reset = rate.reset
        reset_time = reset.replace(tzinfo=timezone.utc) if hasattr(reset, "replace") else datetime.now(timezone.utc)
        return remaining, limit, reset_time
    except Exception:
        return -1, -1, datetime.now(timezone.utc)


def check_gitlab_rate_limit(api: Any) -> tuple[int, int, datetime]:
    """Check GitLab API rate limit. Returns (remaining, limit, reset_time)."""
    try:
        info = api.get_rate_limit()
        remaining = _to_int(info.get("remaining", -1))
        limit = _to_int(info.get("limit", -1))
        reset_ts = info.get("reset", 0)
        reset_time = datetime.fromtimestamp(_to_int(reset_ts), tz=timezone.utc) if _to_int(reset_ts) else datetime.now(timezone.utc)
        return remaining, limit, reset_time
    except Exception:
        return -1, -1, datetime.now(timezone.utc)


def warn_if_near_limit(remaining: int, limit: int, reset_time: datetime, provider: str) -> None:
    """Print a warning to stderr if approaching API rate limit."""
    if limit <= 0 or remaining < 0:
        return
    ratio = remaining / limit
    if ratio < RATE_LIMIT_WARN_THRESHOLD:
        reset_str = reset_time.strftime("%H:%M:%S UTC")
        import sys
        print(
            f"Warning: {provider} API rate limit low ({remaining}/{limit} remaining, resets at {reset_str})",
            file=sys.stderr,
        )
