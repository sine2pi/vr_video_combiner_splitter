# Bolt Journal

## 2026-09-23 - Consolidating ffprobe Metadata and Duration Extraction
**Learning:** `ffprobe` process spawning takes ~70ms on Linux. When video operations retrieve stream info (resolution, fps, codec) and format duration in separate calls, process spawn latency doubles. Consolidating stream and format metadata into a single JSON query with `@functools.lru_cache` and `os.path.abspath(os.path.normpath(...))` path normalization avoids redundant subprocesses and provides instant cache hits across relative and absolute file paths.
**Action:** When probing file metadata, extract all required stream and container format fields in a single query and normalize file paths prior to caching.
