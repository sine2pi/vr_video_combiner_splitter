## 2025-05-14 - Consolidating ffprobe calls
**Learning:** Multiple sequential calls to 'ffprobe' to retrieve different video metadata (fps, codec, resolution) introduce significant overhead due to process spawning. Consolidating these into a single 'ffprobe' call with JSON output and parsing it once is much more efficient.
**Action:** Use a single 'get_video_info' function that returns all necessary metadata in a dictionary.
