import os
import unittest
import subprocess
import time
import queue
import tkinter as tk
from unittest.mock import MagicMock, patch

import convert

class TestConvertAndPerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate dummy video file
        cls.test_video = "test_dummy.mp4"
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=1:size=1280x720:rate=30',
            '-c:v', 'libx264', cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        # Clean up dummy video file
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info_correctness(self):
        # Verify the returned values are correct
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')

    def test_get_video_info_path_normalization_cache(self):
        # Clear lru_cache first to get accurate timing/metrics
        convert._get_video_info_cached.cache_clear()

        # Run first call
        start_time = time.perf_counter()
        info1 = convert.get_video_info(self.test_video)
        time_first = time.perf_counter() - start_time

        # Run subsequent calls with different path representations
        # 1. Relative path
        # 2. Absolute path
        # 3. Path with extra slashes or dots
        abs_path = os.path.abspath(self.test_video)
        dot_path = os.path.join(".", self.test_video)

        # First call to absolute path should hit the cache!
        start_time = time.perf_counter()
        info2 = convert.get_video_info(abs_path)
        time_abs = time.perf_counter() - start_time

        # First call to dot path should also hit the cache!
        start_time = time.perf_counter()
        info3 = convert.get_video_info(dot_path)
        time_dot = time.perf_counter() - start_time

        # Verify correct outputs
        self.assertEqual(info1, info2)
        self.assertEqual(info1, info3)

        # Check cache hits/misses
        hits, misses, maxsize, currsize = convert._get_video_info_cached.cache_info()
        self.assertEqual(misses, 1, "There should be exactly 1 cache miss (first call)")
        self.assertEqual(hits, 2, "There should be exactly 2 cache hits (different path variations)")

        print(f"\n[Performance Report]")
        print(f"First call (miss): {time_first * 1000:.3f} ms")
        print(f"Subsequent absolute path (hit): {time_abs * 1000:.3f} ms")
        print(f"Subsequent relative path (hit): {time_dot * 1000:.3f} ms")
        print(f"Cache Speedup: {time_first / max(time_abs, 1e-9):.1f}x speedup")

    def test_run_process_empty_line_filtering(self):
        # Test that run_process correctly filters out empty / whitespace-only lines
        logged_lines = []
        def log_callback(msg):
            logged_lines.append(msg)

        # Run a simple bash echo command with multiple trailing/empty lines
        cmd = ['python3', '-c', 'print("Hello"); print("   "); print(""); print("World")']
        convert.run_process(cmd, log_callback=log_callback)

        self.assertIn("Hello", logged_lines)
        self.assertIn("World", logged_lines)
        # Ensure none of the empty or whitespace-only lines were logged
        self.assertNotIn("", logged_lines)
        self.assertNotIn("   ", logged_lines)

    @patch('tkinter.Tk')
    def test_app_thread_safe_capped_logging(self, mock_tk):
        # Mock the Tkinter Root Window and Text widget
        mock_root = mock_tk.return_value

        # We need a fake Text widget to ensure insert/delete works and mimics capping
        class FakeText:
            def __init__(self):
                self.content = []
            def config(self, *args, **kwargs):
                pass
            def insert(self, index, text):
                self.content.append(text)
            def delete(self, start, end):
                # Simple line-based deletion for 1.0 to line.0
                if start == '1.0':
                    # Parse line number to delete
                    try:
                        lines_to_del = int(end.split('.')[0])
                        # In Tkinter, delete('1.0', '7.0') deletes lines 1 to 6 (7 - 1 lines)
                        self.content = self.content[lines_to_del - 1:]
                    except Exception:
                        pass
            def index(self, index_str):
                if index_str == 'end-1c':
                    return f"{len(self.content) + 1}.0"
                return "1.0"
            def see(self, index):
                pass
            def pack(self, *args, **kwargs):
                pass
            def yview(self, *args, **kwargs):
                pass

        class FakeStringVar:
            def __init__(self, master=None, value="", name=None):
                self._val = value
            def get(self):
                return self._val
            def set(self, val):
                self._val = val

        # Use patch to mock ttk components in __init__
        with patch('tkinter.StringVar', FakeStringVar), \
             patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.Notebook'), \
             patch('tkinter.ttk.LabelFrame'), \
             patch('tkinter.ttk.Radiobutton'), \
             patch('tkinter.ttk.OptionMenu'), \
             patch('tkinter.ttk.Entry'), \
             patch('tkinter.Text', return_value=FakeText()):

             app = convert.VRSplitCombineApp(mock_root)

             # Verify log_queue is initialized
             self.assertTrue(hasattr(app, 'log_queue'))
             self.assertIsInstance(app.log_queue, queue.Queue)

             # Put some log messages
             app.log("Log Line 1")
             app.log("Log Line 2")

             # Queue should have 2 items
             self.assertEqual(app.log_queue.qsize(), 2)

             # Process the logs via poll_log_queue (mimic Tkinter's callback)
             # Let's mock out self.root.after to prevent infinite loop
             app.root.after = MagicMock()
             app.poll_log_queue()

             # Check that they were inserted into log_text
             self.assertEqual(app.log_text.content, ["Log Line 1\n", "Log Line 2\n"])
             self.assertEqual(app.log_queue.qsize(), 0)

             # Now test capping: add 1005 lines
             app.log_text.content = [f"Line {i}\n" for i in range(1005)]
             app.log("Final Line")
             app.poll_log_queue()

             # After adding, length should be capped to 1000
             self.assertEqual(len(app.log_text.content), 1000)
             self.assertEqual(app.log_text.content[-1], "Final Line\n")

if __name__ == '__main__':
    unittest.main()
