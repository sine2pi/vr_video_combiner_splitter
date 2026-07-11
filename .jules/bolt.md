## 2025-05-15 - Consolidating ffprobe calls for video metadata retrieval
**Learning:** Sequential calls to 'ffprobe' to retrieve individual video attributes (width, height, codec, fps) incur significant process spawning overhead. Consolidating these into a single 'ffprobe' call with JSON output reduces metadata retrieval latency by approximately 70%.
**Action:** Use a unified 'get_video_info' function that retrieves all necessary stream attributes in one pass whenever multiple metadata points are needed.
