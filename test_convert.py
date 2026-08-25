import unittest
from unittest.mock import MagicMock, patch
import os, sys, queue
import convert

class TestConvertOptimizations(unittest.TestCase):

    def test_get_video_info_path_normalization_cache(self):
        """Test that relative and absolute paths map to the same LRU cache entry."""
        dummy_info = {'fps': 30.0, 'codec': 'h264', 'width': 1920, 'height': 1080}

        with patch('convert._get_video_info_cached', return_value=dummy_info) as mock_cached:
            rel_path = './test_video.mp4'
            abs_path = os.path.abspath(os.path.normpath(rel_path))

            res1 = convert.get_video_info(rel_path)
            res2 = convert.get_video_info(abs_path)

            self.assertEqual(res1, dummy_info)
            self.assertEqual(res2, dummy_info)
            # Both calls should map to the exact same normalized absolute path argument
            self.assertEqual(mock_cached.call_count, 2)
            mock_cached.assert_called_with(abs_path)

    def test_run_process_filters_empty_lines(self):
        """Test that run_process filters out empty/whitespace lines from logs."""
        logs = []
        def log_cb(msg):
            logs.append(msg)

        mock_proc = MagicMock()
        mock_proc.stdout = ["Executing ffmpeg\n", "  \n", "frame=100\n", "\n", "frame=200\n"]
        mock_proc.returncode = 0

        with patch('subprocess.Popen', return_value=mock_proc):
            convert.run_process(['echo', 'test'], log_callback=log_cb)

        self.assertIn("Executing: echo test", logs[0])
        self.assertIn("Executing ffmpeg", logs)
        self.assertIn("frame=100", logs)
        self.assertIn("frame=200", logs)
        self.assertNotIn("", logs)
        self.assertNotIn("  ", logs)

    def test_app_queue_logging_and_capping(self):
        """Test that VRSplitCombineApp logs via queue and caps display lines."""
        import tkinter as tk

        root = tk.Tk()
        try:
            app = convert.VRSplitCombineApp(root)

            # Put 105 log messages into app.log
            for i in range(105):
                app.log(f"Log message {i}")

            self.assertFalse(app.log_queue.empty())

            # Manually trigger poll_log_queue once
            app.poll_log_queue()

            # Should have processed 100 messages into log_text
            content = app.log_text.get('1.0', 'end')
            self.assertIn("Log message 0", content)
            self.assertIn("Log message 99", content)
            self.assertNotIn("Log message 100", content)

            # Drain remaining 5 messages
            app.poll_log_queue()
            content2 = app.log_text.get('1.0', 'end')
            self.assertIn("Log message 100", content2)
        finally:
            root.destroy()

if __name__ == '__main__':
    unittest.main()
