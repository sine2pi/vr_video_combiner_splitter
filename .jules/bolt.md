## 2026-08-13 - Thread-Safe Batched Logging in Tkinter
**Learning:** Redirecting process log outputs directly to Tkinter UI controls from background worker threads is a severe thread-safety anti-pattern. Frequent `update_idletasks()` calls on background threads result in extreme rendering lags and potential deadlocks.
**Action:** Offload logging to a thread-safe `queue.Queue`, poll and batch-write log updates every 100ms on the main thread via `root.after()`, and cap the total displayed log lines to prevent unbounded memory usage and redrawing bottlenecks.
