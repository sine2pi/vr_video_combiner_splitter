import unittest
import unittest.mock as mock
import os
import time
import tkinter as tk
import convert

class TestConvertOptimizations(unittest.TestCase):

    def test_get_video_info_path_normalization_cache(self):
        # Mock _get_video_info_cached to verify it is called with normalized path
        dummy_info = {'fps': 30.0, 'codec': 'h264', 'width': 1920, 'height': 1080}

        with mock.patch('convert._get_video_info_cached', return_value=dummy_info) as mock_cached:
            # Query get_video_info with relative and absolute variations
            rel_path = "test_video.mp4"
            dot_path = "./test_video.mp4"
            abs_path = os.path.abspath(rel_path)

            res1 = convert.get_video_info(rel_path)
            res2 = convert.get_video_info(dot_path)
            res3 = convert.get_video_info(abs_path)

            self.assertEqual(res1, dummy_info)
            self.assertEqual(res2, dummy_info)
            self.assertEqual(res3, dummy_info)

            # All variations normalize to the exact same absolute path
            # Therefore _get_video_info_cached is called with abs_path
            mock_cached.assert_called_with(abs_path)

    def test_legacy_wrappers(self):
        dummy_info = {'fps': 60.0, 'codec': 'hevc', 'width': 3840, 'height': 2160}
        with mock.patch('convert.get_video_info', return_value=dummy_info):
            self.assertEqual(convert.frame_rate("sample.mp4"), 60.0)
            self.assertEqual(convert.vcodec("sample.mp4"), "hevc")
            self.assertEqual(convert.vresolution("sample.mp4"), (3840, 2160))

    def test_vr_app_thread_safe_log_queue_and_trimming(self):
        root = tk.Tk()
        root.withdraw() # Hide GUI window for headless testing

        app = convert.VRSplitCombineApp(root)

        # Enqueue multiple log messages from simulated worker threads
        messages = [f"Log line {i}" for i in range(1200)]
        for msg in messages:
            app.log(msg)

        # Before poll_log_queue runs, messages are queued safely
        self.assertFalse(app.log_queue.empty())

        # Trigger poll_log_queue to drain queue on main thread
        app.poll_log_queue()

        # Queue should be empty now
        self.assertTrue(app.log_queue.empty())

        # Verify text widget content is capped to 1000 lines
        log_content = app.log_text.get("1.0", "end-1c").strip().split("\n")
        self.assertLessEqual(len(log_content), 1000)
        self.assertEqual(log_content[-1], "Log line 1199")

        root.destroy()

    def test_run_process_filters_empty_lines(self):
        fake_stdout = ["\n", "  \n", "FFmpeg output line 1\n", "frame=100 fps=60\n", "\n"]
        mock_proc = mock.MagicMock()
        mock_proc.stdout = fake_stdout
        mock_proc.returncode = 0

        logs = []

        with mock.patch('subprocess.Popen', return_value=mock_proc):
            convert.run_process(['ffmpeg', '-version'], log_callback=logs.append)

        # Only non-empty stripped lines should be passed to log_callback
        self.assertEqual(logs, ["Executing: ffmpeg -version", "FFmpeg output line 1", "frame=100 fps=60"])

if __name__ == '__main__':
    unittest.main()
