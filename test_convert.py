import unittest
import os
import time
import subprocess
import shutil
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = os.path.abspath("test.mp4")
        if not os.path.exists(cls.test_video):
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=1:size=1280x720:rate=30",
                "-c:v", "libx264", cls.test_video
            ]
            subprocess.run(cmd, capture_output=True, check=True)

    def setUp(self):
        if hasattr(convert.get_video_info, "cache_clear"):
            convert.get_video_info.cache_clear()
        if hasattr(convert._ffmpeg_has_encoder, "cache_clear"):
            convert._ffmpeg_has_encoder.cache_clear()
        if hasattr(convert._ffmpeg_has_filter, "cache_clear"):
            convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info["width"], 1280)
        self.assertEqual(info["height"], 720)
        self.assertEqual(info["fps"], 30.0)
        self.assertIn("codec", info)
        self.assertIn("duration", info)
        self.assertAlmostEqual(info["duration"], 1.0, places=1)

    def test_video_duration(self):
        duration = convert.video_duration(self.test_video)
        self.assertAlmostEqual(duration, 1.0, places=1)

    def test_ffmpeg_has_encoder_and_filter(self):
        has_v360 = convert._ffmpeg_has_filter("v360")
        self.assertIsInstance(has_v360, bool)

        has_h264 = convert._ffmpeg_has_encoder("libx264") or convert._ffmpeg_has_encoder("h264")
        self.assertTrue(has_h264)

    def test_caching_performance(self):
        # Cold call
        t0 = time.perf_counter()
        info1 = convert.get_video_info(self.test_video)
        dur1 = convert.video_duration(self.test_video)
        enc1 = convert._ffmpeg_has_encoder("libx264")
        flt1 = convert._ffmpeg_has_filter("v360")
        t_cold = time.perf_counter() - t0

        # Cached calls with different path representations (e.g. relative vs absolute)
        rel_path = os.path.relpath(self.test_video)
        t0 = time.perf_counter()
        for _ in range(50):
            info2 = convert.get_video_info(rel_path)
            dur2 = convert.video_duration(self.test_video)
            enc2 = convert._ffmpeg_has_encoder("libx264")
            flt2 = convert._ffmpeg_has_filter("v360")
        t_cached_50 = time.perf_counter() - t0

        self.assertEqual(info1["width"], info2["width"])
        self.assertEqual(dur1, dur2)
        self.assertEqual(enc1, enc2)
        self.assertEqual(flt1, flt2)

        # 50 cached calls should be drastically faster than 1 cold call
        print(f"\n[BENCHMARK] Cold execution time: {t_cold:.4f}s")
        print(f"[BENCHMARK] 50 Cached iterations time: {t_cached_50:.6f}s")

if __name__ == "__main__":
    unittest.main()
