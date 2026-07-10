## 2026-07-10 - Consolidating FFprobe Calls
**Learning:** Sequential calls to 'ffprobe' for different metadata (fps, codec, resolution) incur significant overhead due to multiple process spawns. Consolidating into a single call with JSON output reduced retrieval time by ~68%.
**Action:** Use 'get_video_info' to retrieve all necessary video attributes in one go.
