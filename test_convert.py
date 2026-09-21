import unittest
import time
import os
import shutil
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):

    def setUp(self):
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_ffmpeg_has_encoder_caching(self):
        # Call once to populate cache
        res1 = convert._ffmpeg_has_encoder('libx264')
        info = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(info.hits, 0)
        self.assertEqual(info.misses, 1)

        # Second call should hit cache
        res2 = convert._ffmpeg_has_encoder('libx264')
        self.assertEqual(res1, res2)
        info = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(info.hits, 1)
        self.assertEqual(info.misses, 1)

    def test_ffmpeg_has_filter_caching(self):
        # Call once to populate cache
        res1 = convert._ffmpeg_has_filter('v360')
        info = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(info.hits, 0)
        self.assertEqual(info.misses, 1)

        # Second call should hit cache
        res2 = convert._ffmpeg_has_filter('v360')
        self.assertEqual(res1, res2)
        info = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(info.hits, 1)
        self.assertEqual(info.misses, 1)

    def test_performance_speedup(self):
        convert._ffmpeg_has_encoder.cache_clear()

        # Measure 10 calls with cache
        start_time = time.perf_counter()
        for _ in range(10):
            convert._ffmpeg_has_encoder('libx264')
        cached_duration = time.perf_counter() - start_time

        # Verify hits
        info = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(info.hits, 9)
        self.assertEqual(info.misses, 1)

        # Measure 10 calls without cache (clearing each time)
        start_time = time.perf_counter()
        for _ in range(10):
            convert._ffmpeg_has_encoder.cache_clear()
            convert._ffmpeg_has_encoder('libx264')
        uncached_duration = time.perf_counter() - start_time

        print(f"\n[Benchmark] 10 calls - Cached: {cached_duration*1000:.2f}ms, Uncached: {uncached_duration*1000:.2f}ms")
        self.assertLess(cached_duration, uncached_duration)

if __name__ == '__main__':
    unittest.main()
