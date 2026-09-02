import unittest
import tkinter as tk
import time
import os
import convert

class TestConvertLogging(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = convert.VRSplitCombineApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_log_functionality(self):
        self.app.log("Test log message 1")
        self.app.log("Test log message 2")

        # Process any pending queue/idle events
        if hasattr(self.app, 'poll_log_queue'):
            self.app.poll_log_queue()
        else:
            self.root.update_idletasks()

        log_content = self.app.log_text.get("1.0", tk.END)
        self.assertIn("Test log message 1", log_content)
        self.assertIn("Test log message 2", log_content)

    def test_logging_benchmark(self):
        num_messages = 1000
        start = time.perf_counter()
        for i in range(num_messages):
            self.app.log(f"frame={i} fps=60 q=28.0 size=1024kB time=00:00:{i%60:02d} bitrate=1000.0kbits/s speed=1.5x")

        # Process queued messages if poll_log_queue exists
        if hasattr(self.app, 'poll_log_queue'):
            self.app.poll_log_queue()

        elapsed = time.perf_counter() - start
        print(f"\n[BENCHMARK] Logging {num_messages} messages took {elapsed:.4f} seconds ({elapsed/num_messages*1000:.3f} ms/message)")

if __name__ == '__main__':
    unittest.main()
