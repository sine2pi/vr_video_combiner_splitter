## 2026-08-20 - Normalize File Paths Before LRU Caching
**Learning:** Functions cached via `functools.lru_cache` that accept file paths will treat equivalent relative, absolute, and unnormalized path strings (e.g. `video.mp4` vs `./video.mp4` vs `/abs/path/video.mp4`) as distinct keys, causing cache misses and redundant subprocess calls (e.g. `ffprobe`).
**Action:** Always convert file paths with `os.path.abspath(os.path.normpath(file_path))` before passing them to the underlying LRU-cached function.
