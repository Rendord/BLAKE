from collections import OrderedDict
from typing import Generic, Optional, TypeVar
from threading import Lock

K = TypeVar("K")
V = TypeVar("V")

class LRUCache(Generic[K, V]):
    maxsize: int
    _d: OrderedDict[K, V]
    _lock: Lock

    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self._d = OrderedDict()
        self._lock = Lock()

    def __contains__(self, key: K) -> bool:
        with self._lock:
            return key in self._d

    def get(self, key: K) -> Optional[V]:
        with self._lock:
            if key not in self._d:
                return None
            self._d.move_to_end(key)
            return self._d[key]

    def put(self, key: K, value: V) -> None:
        with self._lock:
            if key in self._d:
                self._d.move_to_end(key)
            self._d[key] = value
            if len(self._d) > self.maxsize:
                self._d.popitem(last=False)  # evict least recent