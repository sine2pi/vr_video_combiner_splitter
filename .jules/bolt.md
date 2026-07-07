## 2025-05-14 - Consolidating ffprobe calls
**Learning:** Multiple sequential calls to 'ffprobe' to retrieve individual metadata fields (fps, codec, resolution) introduces significant overhead due to process spawning. Consolidating these into a single JSON-formatted 'ffprobe' call reduces latency.
**Action:** Implement 'get_video_info' to retrieve all necessary metadata in one pass and refactor calling code to use it.
