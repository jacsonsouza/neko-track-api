import time


class MemoryStateCache:
    def __init__(self):
        self._storage = {}

    def set(self, key, ttl_seconds: int) -> None:
        expire_at = int(time.time()) + ttl_seconds
        self._storage[key] = expire_at

    def pop(self, key: str) -> bool:
        expire_at = self._storage.pop(key, None)

        if expire_at is None:
            return False

        if time.time() > expire_at:
            return False

        return True


state_cache = MemoryStateCache()
