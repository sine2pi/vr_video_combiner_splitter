## 2026-07-04 - [Optimized Video Metadata Retrieval]
**Learning:** Calling ffprobe multiple times for the same file (to get FPS, codec, resolution separately) is highly inefficient due to process spawn overhead.
**Action:** Use a single JSON-formatted ffprobe call to retrieve all necessary metadata in one go. This reduces overhead by ~60%.
