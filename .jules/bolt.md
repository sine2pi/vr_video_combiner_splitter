## 2025-05-15 - Consolidate ffprobe calls
**Learning:** Calling `ffprobe` multiple times to retrieve different metadata (width, height, codec, fps) from the same video file is highly inefficient due to the overhead of spawning new processes. In this Python/Tkinter application, each `subprocess.run` call adds significant delay (~100-150ms per call).
**Action:** Use a single `ffprobe` call with `-show_entries` and `-of json` to retrieve all necessary metadata in one go. This reduces metadata retrieval time by ~80%, which is particularly noticeable in batch processing loops.
