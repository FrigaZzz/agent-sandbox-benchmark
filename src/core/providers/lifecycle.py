"""Bounded benchmark lifetimes and portable ownership labels (never credentials)."""
import re
import time

OWNER = "bench-sandboxes"


def bounded_ttl(value, *, minimum=1, maximum=900):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"Sandbox TTL must be an integer between {minimum} and {maximum} seconds")
    return value


def ttl_seconds(value):
    match = re.fullmatch(r"([1-9][0-9]*)(s|m|h)", str(value))
    if not match:
        raise ValueError("TTL must use positive integer seconds, minutes or hours (e.g. 180s)")
    return bounded_ttl(int(match[1]) * {"s": 1, "m": 60, "h": 3600}[match[2]])


def ownership(run_id):
    return {"benchmark_owner": OWNER, "benchmark_run_id": run_id,
            "benchmark_created_at": str(int(time.time()))}
