# Bolt's Journal

## 2026-06-25 - Sequential Process Spawning for Metadata Retrieval
**Learning:** Sequential calls to `ffprobe` to fetch single properties (`r_frame_rate`, `codec_name`, `width`/`height`) from a single video file multiply the latency of metadata querying by the number of queries. Spawning subprocesses is extremely expensive.
**Action:** Consolidate multiple metadata queries into a single `ffprobe` command that outputs JSON, parse the structured output once, and cache the results using `functools.lru_cache` to eliminate redundant subsequent processes.
