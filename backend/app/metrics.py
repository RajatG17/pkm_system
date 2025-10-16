# backend/app/metrics.py
from __future__ import annotations
import threading, bisect
from collections import defaultdict, deque
from typing import Deque, Dict, List

_lock = threading.Lock()
counters: Dict[str, int] = defaultdict(int)
timers: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=1000))  # store last 1000 ms samples per metric

def incr(name: str, n: int = 1) -> None:
    with _lock:
        counters[name] += n

def observe(name: str, ms: float) -> None:
    # guard against bogus/negative durations
    if ms is None or ms != ms or ms < 0:
        return
    with _lock:
        timers[name].append(ms)

def _percentile(data: List[float], p: float) -> float | None:
    """Nearest-rank percentile (p in [0,1])."""
    if not data:
        return None
    data = sorted(data)
    # nearest-rank index (1-based), clamp to bounds
    rank = max(1, min(len(data), int(round(p * len(data)))))
    return data[rank - 1]

def render_prom() -> str:
    lines: List[str] = []
    with _lock:
        # Counters
        for k, v in counters.items():
            lines.append(f"# TYPE {k} counter")
            lines.append(f"{k} {int(v)}")

        # Timers -> percentiles
        for k, dq in timers.items():
            arr = list(dq)
            p50 = _percentile(arr, 0.50)
            p95 = _percentile(arr, 0.95)
            p99 = _percentile(arr, 0.99)
            for suffix, val in (("p50", p50), ("p95", p95), ("p99", p99)):
                name = f"{k}_{suffix}"
                lines.append(f"# TYPE {name} gauge")
                if val is None:
                    lines.append(f"{name} 0")
                else:
                    lines.append(f"{name} {val:.3f}")
    return "\n".join(lines) + "\n"
