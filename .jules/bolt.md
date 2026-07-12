## 2025-05-15 - Consolidate metadata retrieval
**Learning:** Sequential calls to `ffprobe` for different metadata (fps, codec, resolution) introduce significant latency due to process spawning overhead (approx 0.08s per call).
**Action:** Use a single `ffprobe` call with `-of json` to retrieve all necessary streams info in one go.

## 2025-05-15 - ffprobe error handling
**Learning:** Passing `-v -error` to `ffprobe` is invalid and causes it to fail. The correct flag for error-only output is `-v error`.
**Action:** Always verify `ffprobe` argument syntax in the sandbox if unsure.
