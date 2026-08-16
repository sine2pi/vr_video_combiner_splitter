import unittest
import os
import queue
import tempfile
import tkinter as tk
from unittest.mock import MagicMock, patch

import convert

class TestConvertOptimizations(unittest.TestCase):

    def test_get_video_info_path_normalization(self):
        # Test that path normalization ensures relative and absolute paths resolve to the same cache entry
        convert.get_video_info.cache_clear()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = '{"streams": [{"r_frame_rate": "30000/1001", "codec_name": "h264", "width": 1920, "height": 1080}]}'

            rel_path = 'test_video.mp4'
            abs_path = os.path.abspath(rel_path)

            res1 = convert.get_video_info(rel_path)
            res2 = convert.get_video_info(abs_path)

            self.assertEqual(res1['width'], 1920)
            self.assertEqual(res2['width'], 1920)
            # ffprobe should only be invoked once because the second call hits the LRU cache
            mock_run.assert_called_once()

    def test_run_process_filters_empty_lines(self):
        # Test that empty or whitespace-only lines from stdout are filtered out
        logs = []
        def log_cb(msg):
            logs.append(msg)

        fake_stdout = ["\n", "Processing frame 10\n", "   \n", "Processing frame 20\n", "\n"]

        mock_popen = MagicMock()
        mock_popen.stdout = fake_stdout
        mock_popen.returncode = 0
        mock_popen.wait.return_value = 0

        with patch('subprocess.Popen', return_value=mock_popen):
            convert.run_process(["ffmpeg", "-version"], log_cb)

        expected_logs = [
            "Executing: ffmpeg -version",
            "Processing frame 10",
            "Processing frame 20"
        ]
        self.assertEqual(logs, expected_logs)

    def test_app_log_queue_and_line_capping(self):
        # Test that log messages put into the queue are processed by poll_log_queue and line capping works
        root = tk.Tk()
        root.withdraw()
        try:
            mock_text = MagicMock()
            mock_text.index.return_value = "1005.0"

            with patch('convert.tk.Text', return_value=mock_text):
                app = convert.VRSplitCombineApp(root)

                # Log a message via the thread-safe method
                app.log("Test log entry")
                self.assertFalse(app.log_queue.empty())

                # Call poll_log_queue directly to simulate the Tkinter main loop tick
                app.poll_log_queue()

                self.assertTrue(app.log_queue.empty())
                mock_text.config.assert_any_call(state='normal')
                mock_text.insert.assert_called_with('end', "Test log entry\n")
                # Ensure excess lines were deleted when total lines > 1000 (1005 - 1000 = 5 lines excess)
                mock_text.delete.assert_called_with('1.0', '6.0')
        finally:
            root.destroy()

if __name__ == '__main__':
    unittest.main()
