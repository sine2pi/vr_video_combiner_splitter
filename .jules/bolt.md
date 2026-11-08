# Bolt Journal

## 2026-09-23 - Consolidate FFprobe Metadata and Duration Query
**Learning:** Querying FFprobe stream attributes and container format duration separately spawned multiple subprocesses taking ~80-100ms each per video file. By consolidating stream metadata (`width,height,codec_name,r_frame_rate`) and container duration (`format=duration`) into a single JSON FFprobe call within the LRU-cached `get_video_info` function, cold query latency was cut in half (~148ms to ~76ms) and subsequent `video_duration` checks hit the LRU cache directly in microseconds (<0.002ms).
**Action:** In CLI/media processing applications, consolidate stream and format specifiers into a single probe invocation rather than issuing separate queries per attribute.
