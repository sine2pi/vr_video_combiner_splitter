import unittest
import os
import subprocess
import time
import tempfile
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.video_path = os.path.join(cls.temp_dir.name, "test_video.mp4")
        # Generate dummy 2-second video using ffmpeg
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "testsrc=duration=2:size=1280x720:rate=30",
            "-c:v", "libx264",
            cls.video_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        convert.get_video_info.cache_clear()

    def test_get_video_info_keys_and_values(self):
        info = convert.get_video_info(self.video_path)
        self.assertEqual(info["width"], 1280)
        self.assertEqual(info["height"], 720)
        self.assertEqual(info["fps"], 30.0)
        self.assertIn("h264", info["codec"])
        self.assertAlmostEqual(info["duration"], 2.0, delta=0.5)

    def test_helper_wrappers(self):
        self.assertEqual(convert.frame_rate(self.video_path), 30.0)
        self.assertIn("h264", convert.vcodec(self.video_path))
        self.assertEqual(convert.vresolution(self.video_path), (1280, 720))
        self.assertAlmostEqual(convert.video_duration(self.video_path), 2.0, delta=0.5)

    def test_cache_hit_performance(self):
        # First call populates cache
        t0 = time.perf_counter()
        info1 = convert.get_video_info(self.video_path)
        t1 = time.perf_counter()
        first_call_time = t1 - t0

        # Second call with normalized relative path should hit cache
        rel_path = os.path.relpath(self.video_path)
        t2 = time.perf_counter()
        info2 = convert.get_video_info(rel_path)
        t3 = time.perf_counter()
        second_call_time = t3 - t2

        self.assertEqual(info1, info2)
        # Cached hit should be at least 100x faster than ffprobe execution
        self.assertLess(second_call_time, first_call_time / 10)

    def test_ffmpeg_check_caching(self):
        t0 = time.perf_counter()
        res1 = convert._ffmpeg_has_encoder("hevc_nvenc")
        t1 = time.perf_counter()

        t2 = time.perf_counter()
        res2 = convert._ffmpeg_has_encoder("hevc_nvenc")
        t3 = time.perf_counter()

        self.assertEqual(res1, res2)
        self.assertLess(t3 - t2, (t1 - t0) / 10 if (t1 - t0) > 0.001 else 0.01)

if __name__ == "__main__":
    unittest.main()
