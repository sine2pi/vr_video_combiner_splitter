## 2025-05-15 - Consolidating ffprobe calls
**Learning:** The application was spawning multiple `ffprobe` processes to retrieve different pieces of video metadata (fps, codec, resolution, bitrate) for the same file. Each process spawn adds significant overhead, especially on Windows or when processing many files in batch.
**Action:** Implement a consolidated `get_video_info` function that fetches all required metadata in a single `ffprobe` call using JSON output format.
