## 2025-05-14 - Consolidating ffprobe calls
**Learning:** Sequential 'ffprobe' calls for individual metadata (width, height, codec, fps) introduce significant process spawning overhead. Combining these into a single 'ffprobe' call with '-of json' output is approximately 70% faster per file.
**Action:** Always retrieve all necessary video metadata in a single JSON-formatted 'ffprobe' call to minimize latency, especially in batch operations.
