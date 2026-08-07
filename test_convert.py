import unittest
from unittest.mock import MagicMock, patch
import os
import convert

class TestConvertOptimizations(unittest.TestCase):

    @patch('convert.subprocess.run')
    def test_get_video_info_path_normalization_cache(self, mock_run):
        # Reset the cache first to ensure a clean state
        convert._get_video_info_cached.cache_clear()

        # Set up a mock response from subprocess.run
        mock_result = MagicMock()
        mock_result.stdout = '{"streams": [{"width": 1920, "height": 1080, "codec_name": "hevc", "r_frame_rate": "60/1"}]}'
        mock_run.return_value = mock_result

        # Define equivalent paths (relative, absolute, with extra separators)
        path1 = "./test_video.mp4"
        path2 = "test_video.mp4"
        path3 = os.path.abspath("test_video.mp4")
        path4 = os.path.join(os.getcwd(), "test_video.mp4")

        # Query all equivalent paths
        res1 = convert.get_video_info(path1)
        res2 = convert.get_video_info(path2)
        res3 = convert.get_video_info(path3)
        res4 = convert.get_video_info(path4)

        # All results should be identical
        self.assertEqual(res1['width'], 1920)
        self.assertEqual(res1['height'], 1080)
        self.assertEqual(res1['codec'], 'hevc')
        self.assertEqual(res1['fps'], 60.0)

        self.assertEqual(res1, res2)
        self.assertEqual(res1, res3)
        self.assertEqual(res1, res4)

        # Subprocess.run should have been called exactly ONCE due to path normalization hitting the cache
        self.assertEqual(mock_run.call_count, 1)

        # Clear cache again for safety
        convert._get_video_info_cached.cache_clear()

    def test_app_queue_logging_thread_safety(self):
        # Since we do not have a DISPLAY environment, we mock the Tkinter root and widgets
        # to test VRSplitCombineApp logging and queue polling.
        mock_root = MagicMock()

        # Mock ttk and tk objects used in VRSplitCombineApp initialization
        with patch('convert.tk.Text') as mock_text_cls, \
             patch('convert.ttk.Frame'), \
             patch('convert.ttk.Label'), \
             patch('convert.ttk.Button'), \
             patch('convert.ttk.Notebook'), \
             patch('convert.ttk.Scrollbar'), \
             patch('convert.ttk.LabelFrame'), \
             patch('convert.ttk.Entry'), \
             patch('convert.ttk.Radiobutton'), \
             patch('convert.ttk.OptionMenu'), \
             patch('convert.tk.StringVar'):

            # Instantiate mock_text instance
            mock_text_inst = MagicMock()
            mock_text_cls.return_value = mock_text_inst

            # Initialize VRSplitCombineApp
            app = convert.VRSplitCombineApp(mock_root)

            # Check that log_queue exists
            self.assertTrue(hasattr(app, 'log_queue'))

            # Initially queue should be empty
            self.assertTrue(app.log_queue.empty())

            # Call log which should put messages in the queue (no direct widget modification or update_idletasks)
            app.log("Test log message 1")
            app.log("Test log message 2")

            # Queue should contain 2 messages
            self.assertEqual(app.log_queue.qsize(), 2)

            # Widget state should NOT have been updated yet (non-blocking)
            mock_text_inst.insert.assert_not_called()

            # Now manually run poll_log_queue to simulate the Tkinter main thread timer execution
            app.poll_log_queue()

            # Queue should be empty now
            self.assertTrue(app.log_queue.empty())

            # The text widget should have been updated with the batched messages
            mock_text_inst.config.assert_any_call(state='normal')
            mock_text_inst.insert.assert_called_with('end', "Test log message 1\nTest log message 2\n")
            mock_text_inst.config.assert_any_call(state='disabled')

            # Ensure self.root.after is called to reschedule the polling
            mock_root.after.assert_called_with(100, app.poll_log_queue)

if __name__ == '__main__':
    unittest.main()
