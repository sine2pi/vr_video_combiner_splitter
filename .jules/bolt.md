## 2025-01-24 - Consolidated Metadata Retrieval
**Learning:** Sequential `ffprobe` calls for different attributes (fps, codec, resolution) are highly inefficient in Python as each spawns a new process. Using a single `ffprobe` call with `-of json` and `-show_entries` to retrieve all required metadata at once reduced latency by ~70% (from ~0.25s to ~0.07s per file).
**Action:** Always prefer a single consolidated JSON-formatted `ffprobe` call over multiple CSV or specialized calls when multiple attributes are needed from the same media file.
