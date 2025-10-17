from __future__ import annotations
from collections import OrderedDict
import threading
from typing import Hashable, Any, Callable

class LRU:
    def __init__(self, size=256):
        self.size = size
        self._d: OrderedDict[Hashable, Any] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, k):
        with self._lock:
            if k in self._d:
                self._d.move_to_end(k)
                return self._d[k]
            return None
    
    def set(self, k, v):
        with self._lock:
            self._d[k] = v
            self._d.move_to_end(k)
            if len(self._d) > self.size:
                self._d.popitem(last=False)

embed_cache = LRU(256)
qa_cache = LRU(128)
search_cache = LRU(128)

