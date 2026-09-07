import unittest
from unittest.mock import patch
import time
import convert

class TestFFmpegFeatureCache(unittest.TestCase):
    def setUp(self):
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_ffmpeg_has_encoder_cached(self):
        with patch('subprocess.run', wraps=convert.subprocess.run) as mock_run:
            res1 = convert._ffmpeg_has_encoder("libx264")
            res2 = convert._ffmpeg_has_encoder("libx264")
            res3 = convert._ffmpeg_has_encoder("libx264")

            self.assertEqual(res1, res2)
            self.assertEqual(res2, res3)
            # Only 1 subprocess call should be made because results are cached
            self.assertEqual(mock_run.call_count, 1)

    def test_ffmpeg_has_filter_cached(self):
        with patch('subprocess.run', wraps=convert.subprocess.run) as mock_run:
            res1 = convert._ffmpeg_has_filter("v360")
            res2 = convert._ffmpeg_has_filter("v360")
            res3 = convert._ffmpeg_has_filter("v360")

            self.assertEqual(res1, res2)
            self.assertEqual(res2, res3)
            # Only 1 subprocess call should be made because results are cached
            self.assertEqual(mock_run.call_count, 1)

    def test_performance_speedup(self):
        # Warm cache
        convert._ffmpeg_has_encoder("hevc_nvenc")
        convert._ffmpeg_has_filter("v360")

        # Time cached calls
        t0 = time.perf_counter()
        for _ in range(100):
            convert._ffmpeg_has_encoder("hevc_nvenc")
            convert._ffmpeg_has_filter("v360")
        t1 = time.perf_counter()

        cached_duration = t1 - t0
        # 100 iterations of cached calls should complete under 1 millisecond (0.001s)
        self.assertLess(cached_duration, 0.01)

if __name__ == '__main__':
    unittest.main()
