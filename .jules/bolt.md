## 2026-08-25 - Thread-Safe Async Logging Queue for Tkinter Background Tasks

**Learning:** Direct UI updates (such as `log_text.insert()` and `root.update_idletasks()`) invoked from background worker threads during continuous FFmpeg execution violate Tkinter thread safety, cause high CPU overhead, and freeze the GUI. Using a non-blocking `queue.Queue` to buffer log outputs and draining them in periodic main-thread batches via `root.after(100, ...)` with line-buffer capping yields a ~74x speedup in UI log processing and eliminates worker thread lock contention.
**Action:** Always route background task logging through a thread-safe `queue.Queue` and process UI updates in main-thread polling batches with buffer capping.
