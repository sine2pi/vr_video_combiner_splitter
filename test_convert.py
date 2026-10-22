import unittest
import os
import subprocess
import time
import shutil
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_file = os.path.abspath('test_sample.mp4')
        if not os.path.exists(cls.test_file):
            cmd = [
                convert.FFMPEG_BIN, '-y',
                '-f', 'lavfi', '-i', 'testsrc=duration=1:size=640x480:rate=30',
                '-c:v', 'libx264',
                cls.test_file
            ]
            subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_structure(self):
        info = convert.get_video_info(self.test_file)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)
        self.assertGreater(info['fps'], 0)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 480)
        self.assertGreater(info['duration'], 0)

    def test_video_duration_uses_get_video_info(self):
        duration = convert.video_duration(self.test_file)
        info = convert.get_video_info(self.test_file)
        self.assertEqual(duration, info['duration'])

    def test_path_normalization_cache_hit(self):
        rel_path = os.path.relpath(self.test_file)
        rel_dot_path = os.path.join('.', rel_path)

        # First call populates cache
        info1 = convert.get_video_info(self.test_file)
        cache_info_before = convert.get_video_info.cache_info()

        # Relative paths should hit cache
        info2 = convert.get_video_info(rel_path)
        info3 = convert.get_video_info(rel_dot_path)
        cache_info_after = convert.get_video_info.cache_info()

        self.assertEqual(info1, info2)
        self.assertEqual(info1, info3)
        self.assertEqual(cache_info_after.hits - cache_info_before.hits, 2)

    def test_cache_clear(self):
        convert.get_video_info(self.test_file)
        self.assertGreater(convert.get_video_info.cache_info().currsize, 0)
        convert.get_video_info.cache_clear()
        self.assertEqual(convert.get_video_info.cache_info().currsize, 0)

    def test_ffmpeg_has_encoder_caching(self):
        # Call 1: Populates cache
        t0 = time.perf_counter()
        res1 = convert._ffmpeg_has_encoder('h264')
        t1 = time.perf_counter()

        # Call 2: Cache hit
        res2 = convert._ffmpeg_has_encoder('h264')
        t2 = time.perf_counter()

        self.assertEqual(res1, res2)
        uncached_time = (t1 - t0) * 1000
        cached_time = (t2 - t1) * 1000
        print(f"\n[Benchmark] _ffmpeg_has_encoder uncached: {uncached_time:.2f}ms, cached: {cached_time:.4f}ms")
        self.assertEqual(convert._ffmpeg_has_encoder.cache_info().hits, 1)

    def test_ffmpeg_has_filter_caching(self):
        # Call 1: Populates cache
        res1 = convert._ffmpeg_has_filter('v360')
        # Call 2: Cache hit
        res2 = convert._ffmpeg_has_filter('v360')
        self.assertEqual(res1, res2)
        self.assertEqual(convert._ffmpeg_has_filter.cache_info().hits, 1)

    def test_invalid_file_fallback(self):
        info = convert.get_video_info('non_existent_file.mp4')
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'unknown')
        self.assertEqual(info['width'], 0)
        self.assertEqual(info['height'], 0)
        self.assertEqual(info['duration'], 0.0)
        self.assertEqual(convert.video_duration('non_existent_file.mp4'), 0.0)

if __name__ == '__main__':
    unittest.main()
