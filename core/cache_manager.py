from __future__ import annotations

import hashlib
from pathlib import Path


class CacheManager:
    """Module-scoped markdown cache manager."""

    DEFAULT_MODULE_DIRS = (
        "business",
        "brain",
        "cto",
        "backend",
        "frontend",
        "landing",
        "roadmap",
    )

    def __init__(self, root: Path | None = None) -> None:
        base = root or Path(__file__).resolve().parents[1]
        self.cache_root = base / "cache"
        self.cache_root.mkdir(parents=True, exist_ok=True)
        for module_dir in self.DEFAULT_MODULE_DIRS:
            (self.cache_root / module_dir).mkdir(parents=True, exist_ok=True)

    def get_cached(self, module: str, prompt: str) -> str | None:
        cache_file = self._cache_file(module, prompt)
        if cache_file.exists():
            print("[CACHE HIT]")
            return cache_file.read_text(encoding="utf-8")
        print("[CACHE MISS]")
        return None

    def set_cached(self, module: str, prompt: str, content: str) -> Path:
        cache_file = self._cache_file(module, prompt)
        cache_file.write_text(content, encoding="utf-8")
        return cache_file

    def clear(self) -> int:
        removed = 0
        for file_path in self.cache_root.rglob("*.md"):
            file_path.unlink(missing_ok=True)
            removed += 1
        return removed

    def _cache_file(self, module: str, prompt: str) -> Path:
        module_dir = self.cache_root / self._normalize_module(module)
        module_dir.mkdir(parents=True, exist_ok=True)
        cache_key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return module_dir / f"{cache_key}.md"

    @staticmethod
    def _normalize_module(module: str) -> str:
        normalized = module.strip().lower()
        if not normalized:
            return "generic"
        return normalized.replace(" ", "_")
