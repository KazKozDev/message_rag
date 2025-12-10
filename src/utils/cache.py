"""File-based cache for LLM responses."""

import hashlib
import json
import time
from pathlib import Path


class ResponseCache:
    """File-based cache for LLM responses."""

    def __init__(self, cache_dir: str = "data/cache", ttl_seconds: int = 3600) -> None:
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files.
            ttl_seconds: Time-to-live for cache entries in seconds.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model.

        Args:
            prompt: The prompt text.
            model: Model name.

        Returns:
            Cache key as hex string.
        """
        key_str = f"{model}:{prompt}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache entry.

        Args:
            cache_key: Cache key.

        Returns:
            Path to cache file.
        """
        return self.cache_dir / f"{cache_key}.json"

    def get(self, prompt: str, model: str) -> str | None:
        """Retrieve cached response.

        Args:
            prompt: The prompt text.
            model: Model name.

        Returns:
            Cached response if found and valid, None otherwise.
        """
        cache_key = self._get_cache_key(prompt, model)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                data = json.load(f)

            # Check if cache entry is expired
            if time.time() - data["timestamp"] > self.ttl_seconds:
                cache_path.unlink()  # Delete expired entry
                return None

            return data["response"]
        except (json.JSONDecodeError, KeyError):
            # Corrupted cache entry
            cache_path.unlink()
            return None

    def set(self, prompt: str, model: str, response: str) -> None:
        """Store response in cache.

        Args:
            prompt: The prompt text.
            model: Model name.
            response: Response to cache.
        """
        cache_key = self._get_cache_key(prompt, model)
        cache_path = self._get_cache_path(cache_key)

        data = {
            "timestamp": time.time(),
            "prompt": prompt,
            "model": model,
            "response": response,
        }

        with open(cache_path, "w") as f:
            json.dump(data, f)

    def clear(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries cleared.
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count

    def clear_expired(self) -> int:
        """Clear expired cache entries.

        Returns:
            Number of entries cleared.
        """
        count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                if current_time - data["timestamp"] > self.ttl_seconds:
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError):
                cache_file.unlink()
                count += 1

        return count
