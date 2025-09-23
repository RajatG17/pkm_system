import time, threading 
from collections import defaultdict

_lock = threading.Lock()
counters = defaultdict(int)
timers = defaultdict(list)

def incr(name: str, n=1):
    with _lock:
        counters[name] += n

def observe(name: str, ms: float):
    with _lock:
        timers[name].append(ms)
        if len(timers[name]) > 500:
            timers[name] = timers[name][-500:]

def render_prom():
    lines = []
    with _lock:
        for k,v in counters.items():
            lines.append(f"# TYPE {k} counter")
            lines.append(f"{k} {v}")
        for k, arr in timers.items():
            if not arr:
                continue
            p50 = sorted(arr)[int(0.50*len(arr)-1)]
            p95 = sorted(arr)[int(0.95*len(arr)-1)]
            p99 = sorted(arr)[int(0.99*len(arr)-1)]
            lines.append(f"# TYPE {k}_p50 gauge")
            lines.append(f"{k}_50 {p50:.3f}")
            lines.append(f"{k}_p95 gauge")
            lines.append(f"{k}_p95 {p95:.3f}")
            lines.append(f"{k}_p99 gauge")
            lines.append(f"{k}_p99 {p99:.3f}")
    return "\n".join(lines) + "\n"


 
