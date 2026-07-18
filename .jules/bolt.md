# Bolt's Journal - Critical Learnings

## 2026-06-25 - Consolidating metadata retrieval with caching
**Learning:** Sequential, independent `ffprobe` calls for retrieving video properties (fps, resolution, and codec) spawn multiple subprocesses, creating significant latency (~150ms-300ms per call). This can be optimized by fetching all metadata at once via a single JSON-formatted `ffprobe` call and using `@functools.lru_cache` to cache the results.
**Action:** Consolidate `frame_rate`, `vcodec`, and `vresolution` to query a cached `get_video_info` function.
