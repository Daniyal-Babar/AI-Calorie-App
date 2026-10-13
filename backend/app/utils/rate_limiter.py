import time
from collections import defaultdict
from flask import request
from app.utils.errors import AppError

# In-memory sliding window rate limiter
_request_records = defaultdict(list)

def check_rate_limit(key: str, max_requests: int = 60, window_seconds: int = 60):
    now = time.time()
    timestamps = _request_records[key]
    # Remove timestamps older than window
    _request_records[key] = [t for t in timestamps if now - t < window_seconds]
    if len(_request_records[key]) >= max_requests:
        raise AppError("Rate limit exceeded. Please wait a moment before sending more messages.", status_code=429)
    _request_records[key].append(now)
