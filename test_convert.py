import unittest
import os
import tempfile
import subprocess
import time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.video_path = os.path.join(cls.temp_dir.name, "test_sample.mp4")
        # Generate 1-second dummy video with 1280x720 30fps h264
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            "testsrc=duration=1:size=1280x720:rate=30",
            "-c:v", "libx264", cls.video_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_and_wrappers(self):
        info = convert.get_video_info(self.video_path)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertIn('h264', info['codec'].lower())
        self.assertAlmostEqual(info['fps'], 30.0, delta=0.1)
        self.assertAlmostEqual(info['duration'], 1.0, delta=0.1)

        self.assertAlmostEqual(convert.frame_rate(self.video_path), 30.0, delta=0.1)
        self.assertEqual(convert.vresolution(self.video_path), (1280, 720))
        self.assertAlmostEqual(convert.video_duration(self.video_path), 1.0, delta=0.1)

    def test_path_normalization_cache_hit(self):
        rel_path = os.path.relpath(self.video_path)
        convert.get_video_info(self.video_path)

        info_before = convert.get_video_info.cache_info()
        convert.get_video_info(rel_path)
        info_after = convert.get_video_info.cache_info()

        self.assertEqual(info_after.hits, info_before.hits + 1)

    def test_ffmpeg_feature_checks_caching(self):
        res1 = convert._ffmpeg_has_encoder("libx264")
        info_before = convert._ffmpeg_has_encoder.cache_info()
        res2 = convert._ffmpeg_has_encoder("libx264")
        info_after = convert._ffmpeg_has_encoder.cache_info()

        self.assertEqual(res1, res2)
        self.assertEqual(info_after.hits, info_before.hits + 1)

        res_f1 = convert._ffmpeg_has_filter("v360")
        f_before = convert._ffmpeg_has_filter.cache_info()
        res_f2 = convert._ffmpeg_has_filter("v360")
        f_after = convert._ffmpeg_has_filter.cache_info()

        self.assertEqual(res_f1, res_f2)
        self.assertEqual(f_after.hits, f_before.hits + 1)

    def test_performance_benchmark(self):
        # Measure uncached vs cached speed
        t0 = time.perf_counter()
        convert.get_video_info(self.video_path)
        uncached_time = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        convert.get_video_info(self.video_path)
        cached_time = (time.perf_counter() - t0) * 1000

        print(f"\n[Benchmark] get_video_info Uncached: {uncached_time:.2f} ms | Cached: {cached_time:.4f} ms")
        self.assertLess(cached_time, uncached_time)

if __name__ == "__main__":
    unittest.main()
