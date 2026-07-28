## 2026-06-21 - Consolidating ffprobe Metadata Retrieval with LRU Cache

**Learning:** Sequential subprocess spawns (such as calling `ffprobe` multiple times to fetch different video metadata properties like width, height, codec, and fps) present a severe performance bottleneck. Consolidating multiple metadata queries into a single JSON-formatted `ffprobe` call reduces first-run retrieval latency by more than 50% (~0.36s to ~0.17s). Adding `@functools.lru_cache(maxsize=128)` completely eliminates subprocess spawning overhead on subsequent queries, reducing latency to virtually 0.

**Action:** Whenever retrieving file or stream metadata via command line tools (like ffprobe, git, etc.), always query all required fields in a single consolidated call, structure the output (e.g. as JSON) for easy parsing, and cache the result using memory-efficient caching mechanisms.
