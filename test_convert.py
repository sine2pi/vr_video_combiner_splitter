import unittest
import time
import os
import tempfile
import convert

class TestConvertOptimizations(unittest.TestCase):

    def setUp(self):
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_ffmpeg_has_encoder_caching(self):
        # Initial call should be a cache miss
        result1 = convert._ffmpeg_has_encoder('hevc_nvenc')
        info1 = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(info1.misses, 1)

        # Second call should be a cache hit
        result2 = convert._ffmpeg_has_encoder('hevc_nvenc')
        info2 = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(result1, result2)
        self.assertEqual(info2.hits, 1)

    def test_ffmpeg_has_filter_caching(self):
        # Initial call should be a cache miss
        result1 = convert._ffmpeg_has_filter('v360')
        info1 = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(info1.misses, 1)

        # Second call should be a cache hit
        result2 = convert._ffmpeg_has_filter('v360')
        info2 = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(result1, result2)
        self.assertEqual(info2.hits, 1)

    def test_find_video_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, 'video1.mp4')
            f2 = os.path.join(tmpdir, 'video2.mkv')
            f3 = os.path.join(tmpdir, 'video_mask.mp4')
            f4 = os.path.join(tmpdir, 'image.jpg')
            for f in (f1, f2, f3, f4):
                open(f, 'w').close()

            files = convert.find_video_files(tmpdir, exclude_substrings=['_mask'])
            self.assertEqual(len(files), 2)
            self.assertIn(f1, files)
            self.assertIn(f2, files)
            self.assertNotIn(f3, files)

    def test_performance_benchmark(self):
        convert._ffmpeg_has_encoder.cache_clear()

        t0 = time.perf_counter()
        convert._ffmpeg_has_encoder('hevc_nvenc')
        uncached_time = time.perf_counter() - t0

        t1 = time.perf_counter()
        for _ in range(100):
            convert._ffmpeg_has_encoder('hevc_nvenc')
        cached_time = (time.perf_counter() - t1) / 100

        print(f'\n[BENCHMARK] Uncached: {uncached_time * 1000:.3f}ms | Cached avg: {cached_time * 1000:.4f}ms')
        self.assertLess(cached_time, uncached_time)

if __name__ == '__main__':
    unittest.main()
