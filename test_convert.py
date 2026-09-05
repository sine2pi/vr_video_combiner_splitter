import unittest
import os
import subprocess
import tkinter as tk
import convert

class TestConvert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = os.path.abspath("test_dummy.mp4")
        if not os.path.exists(cls.test_video):
            cmd = [
                'ffmpeg', '-y', '-f', 'lavfi',
                '-i', 'testsrc=duration=1:size=640x360:rate=30',
                '-c:v', 'libx264', cls.test_video
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            try:
                os.remove(cls.test_video)
            except Exception:
                pass

    def test_get_video_info_path_normalization(self):
        convert._get_video_info_cached.cache_clear()

        rel_path_1 = "test_dummy.mp4"
        rel_path_2 = "./test_dummy.mp4"
        abs_path = os.path.abspath(rel_path_1)

        info1 = convert.get_video_info(rel_path_1)
        cache_after_1 = convert._get_video_info_cached.cache_info()

        info2 = convert.get_video_info(rel_path_2)
        cache_after_2 = convert._get_video_info_cached.cache_info()

        info3 = convert.get_video_info(abs_path)
        cache_after_3 = convert._get_video_info_cached.cache_info()

        self.assertEqual(info1['width'], 640)
        self.assertEqual(info1['height'], 360)
        self.assertEqual(info1, info2)
        self.assertEqual(info2, info3)

        # First call was a miss, subsequent equivalent path calls must be hits
        self.assertEqual(cache_after_1.hits, 0)
        self.assertEqual(cache_after_1.misses, 1)
        self.assertEqual(cache_after_2.hits, 1)
        self.assertEqual(cache_after_3.hits, 2)

    def test_legacy_wrappers(self):
        fps = convert.frame_rate(self.test_video)
        codec = convert.vcodec(self.test_video)
        width, height = convert.vresolution(self.test_video)

        self.assertEqual(fps, 30.0)
        self.assertEqual(codec, "h264")
        self.assertEqual((width, height), (640, 360))

    def test_run_process_filtering(self):
        logs = []
        cmd = ['echo', 'line1\n\nline2\n  \nline3']
        convert.run_process(cmd, log_callback=logs.append)

        self.assertIn("line1", logs)
        self.assertIn("line2", logs)
        self.assertIn("line3", logs)
        self.assertNotIn("", logs)

    def test_app_log_queue_and_capping(self):
        root = tk.Tk()
        try:
            root.withdraw()
            app = convert.VRSplitCombineApp(root)

            # Log 1200 messages
            for i in range(1200):
                app.log(f"Message {i}")

            app.poll_log_queue()

            # Verify queue drained
            self.assertTrue(app.log_queue.empty())

            # Verify logged line count is capped to at most 1000 lines
            line_count = int(app.log_text.index('end-1c').split('.')[0])
            actual_logged_lines = line_count - 1 if line_count > 0 else 0
            self.assertLessEqual(actual_logged_lines, 1000)
            self.assertGreater(actual_logged_lines, 0)
        finally:
            root.destroy()

if __name__ == '__main__':
    unittest.main()
