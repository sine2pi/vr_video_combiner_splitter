import unittest
import os
import subprocess
import time
import functools
import shutil
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_dummy.mp4"
        # Generate a small 2-second dummy video file for testing
        cmd = [
            convert.FFMPEG_BIN, "-y",
            "-f", "lavfi", "-i", "testsrc=duration=2:size=640x360:rate=30",
            "-c:v", "libx264",
            cls.test_video
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertIn('h264', info['codec'].lower())
        self.assertAlmostEqual(info['duration'], 2.0, delta=0.5)

    def test_video_duration_wrapper(self):
        duration = convert.video_duration(self.test_video)
        self.assertAlmostEqual(duration, 2.0, delta=0.5)

    def test_path_normalization_cache_hit(self):
        abs_path = os.path.abspath(self.test_video)
        rel_path = f"./{self.test_video}"

        info1 = convert.get_video_info(rel_path)
        info2 = convert.get_video_info(abs_path)

        cache_info = convert.get_video_info.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(info1, info2)

    def test_ffmpeg_encoder_and_filter_cache(self):
        self.assertTrue(convert._ffmpeg_has_encoder("libx264"))
        hits_before = convert._ffmpeg_has_encoder.cache_info().hits
        self.assertTrue(convert._ffmpeg_has_encoder("libx264"))
        hits_after = convert._ffmpeg_has_encoder.cache_info().hits
        self.assertEqual(hits_after, hits_before + 1)

    def test_performance_benchmark(self):
        # Measure cold vs warm call timing for get_video_info
        t0 = time.perf_counter()
        convert.get_video_info(self.test_video)
        t1 = time.perf_counter()
        cold_time = t1 - t0

        t2 = time.perf_counter()
        convert.get_video_info(self.test_video)
        t3 = time.perf_counter()
        warm_time = t3 - t2

        print(f"\n[BENCHMARK] get_video_info cold: {cold_time*1000:.2f}ms, warm: {warm_time*1000:.2f}ms")
        self.assertLess(warm_time, cold_time)

if __name__ == '__main__':
    unittest.main()
