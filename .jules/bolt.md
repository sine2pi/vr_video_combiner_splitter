# Bolt's Journal - Critical Learnings Only

## 2026-06-21 - Consolidating ffprobe calls
**Learning:** Multiple sequential `ffprobe` process spawns are a major bottleneck for video processing scripts, especially on platforms with high process creation latency. Querying frame rate, codec, and resolution sequentially took 3 separate process invocations.
**Action:** Consolidate multiple metadata queries into a single JSON-formatted `ffprobe` call, and decorate it with `@functools.lru_cache` to cache results. This reduces sequential executions and latency.
