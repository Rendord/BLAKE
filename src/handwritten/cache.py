from collections import OrderedDict
from typing import Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")

#TODO add locking if we upscale to multiple threads
class LRUCache(Generic[K, V]):
    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self._d: OrderedDict[K, V] = OrderedDict()

    def __contains__(self, key: K) -> bool:
        return key in self._d

    def get(self, key: K) -> Optional[V]:
        if key not in self._d:
            return None
        self._d.move_to_end(key)
        return self._d[key]

    def put(self, key: K, value: V) -> None:
        if key in self._d:
            self._d.move_to_end(key)
        self._d[key] = value
        if len(self._d) > self.maxsize:
            self._d.popitem(last=False)  # evict least recent