## 2026-06-21 - Consolidating metadata retrieval saves 3x process spawning overhead
**Learning:** Sequential calls to `ffprobe` to query frame rate, codec, and resolution create significant latency due to OS-level process spawning. Consolidating into a single JSON query and caching with `lru_cache` virtually eliminates subsequent latency and speeds up the initial query by ~3x.
**Action:** Always combine multi-query metadata lookups into a single JSON-based parser call and apply aggressive caching where input values (like file paths) are deterministic.
