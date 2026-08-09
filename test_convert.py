import unittest
from unittest.mock import patch, MagicMock
import os
import convert

class MockVar:
    def __init__(self, value=""):
        self._val = value
    def get(self):
        return self._val
    def set(self, val):
        self._val = val

class TestConvertOptimization(unittest.TestCase):
    @patch('convert.subprocess.run')
    def test_get_video_info_path_normalization_caching(self, mock_run):
        # Clear cache first to have a clean state
        convert._get_video_info_cached.cache_clear()

        # Prepare a mock output from ffprobe
        mock_result = MagicMock()
        mock_result.stdout = '{"streams": [{"width": 1920, "height": 1080, "codec_name": "hevc", "r_frame_rate": "30/1"}]}'
        mock_run.return_value = mock_result

        # Define equivalent path inputs
        path1 = "video.mp4"
        path2 = "./video.mp4"
        path3 = os.path.abspath("video.mp4")

        # Call get_video_info on all three paths
        res1 = convert.get_video_info(path1)
        res2 = convert.get_video_info(path2)
        res3 = convert.get_video_info(path3)

        # Check that they returned identical correct content
        self.assertEqual(res1['width'], 1920)
        self.assertEqual(res2['codec'], 'hevc')
        self.assertEqual(res3['fps'], 30.0)

        # Verify that the subprocess was run exactly ONCE because of cache hit
        self.assertEqual(mock_run.call_count, 1)

    def test_log_queue_thread_safety_and_batching(self):
        # Create a mock Tk root and patch VRSplitCombineApp initialization
        mock_root = MagicMock()
        # Stub the after method
        after_calls = []
        mock_root.after = lambda ms, callback: after_calls.append((ms, callback))

        # Stub the tkinter Tk/Toplevel creation to avoid headless Tkinter errors
        with patch('convert.tk.Text'), patch('convert.ttk.Frame'), patch('convert.ttk.Label'), \
             patch('convert.ttk.Button'), patch('convert.ttk.Notebook'), patch('convert.ttk.LabelFrame'), \
             patch('convert.ttk.Scrollbar'), patch('convert.get_text', side_effect=lambda x: x), \
             patch('convert.tk.StringVar', side_effect=MockVar), patch('convert.ttk.OptionMenu'), \
             patch('convert.ttk.Radiobutton'):

            app = convert.VRSplitCombineApp(mock_root)

            # Initially, should be scheduled to poll
            self.assertTrue(hasattr(app, 'log_queue'))
            self.assertEqual(len(after_calls), 1)
            self.assertEqual(after_calls[0][0], 100)

            # Put some logs in from background thread (app.log is thread-safe)
            app.log("Line 1")
            app.log("Line 2")

            # Verify they are in the queue and text widget hasn't been written to directly yet
            self.assertEqual(app.log_queue.qsize(), 2)
            app.log_text.insert.assert_not_called()

            # Clear scheduled calls to trace the next one
            after_calls.clear()

            # Run poll_log_queue directly to simulate the periodic callback
            app.poll_log_queue()

            # Verify batch insert was called once with the joined lines
            # First line, then second line insert calls
            self.assertEqual(app.log_text.insert.call_count, 2)
            app.log_text.insert.assert_any_call('end', "Line 1\n")
            app.log_text.insert.assert_any_call('end', "Line 2\n")

            # Verify it scheduled the next poll
            self.assertEqual(len(after_calls), 1)
            self.assertEqual(after_calls[0][0], 100)

if __name__ == '__main__':
    unittest.main()
