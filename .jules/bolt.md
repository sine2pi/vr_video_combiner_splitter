## 2026-06-25 - [Path Normalization and Queue-Based Logging]
**Learning:** Normalizing file paths prior to caching metadata retrieval avoids redundant disk/subprocess access for equivalent files. Implementing a thread-safe, non-blocking queue polling mechanism for GUI logging prevents main-thread blocking and thread-safety violations during massive batch/threaded conversions.
**Action:** Always wrap cached functions with path normalization layers when dealing with file inputs, and delegate GUI logging to thread-safe polling patterns like root.after with queue.Queue.
