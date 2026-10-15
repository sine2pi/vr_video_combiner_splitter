import unittest
import os
import tempfile
import subprocess
import time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a dummy test video if ffmpeg is available
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_video = os.path.join(cls.temp_dir.name, "test.mp4")
        try:
            cmd = [
                convert.FFMPEG_BIN,
                "-f", "lavfi", "-i", "testsrc=duration=1:size=640x360:rate=30",
                "-c:v", "libx264", "-y", cls.test_video
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            cls.has_video = True
        except Exception:
            cls.has_video = False

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_ffmpeg_has_encoder_caching(self):
        # Clear cache first
        convert._ffmpeg_has_encoder.cache_clear()
        info_before = convert._ffmpeg_has_encoder.cache_info()

        res1 = convert._ffmpeg_has_encoder('libx264')
        res2 = convert._ffmpeg_has_encoder('libx264')
        info_after = convert._ffmpeg_has_encoder.cache_info()

        self.assertEqual(res1, res2)
        self.assertGreaterEqual(info_after.hits, 1)

    def test_ffmpeg_has_filter_caching(self):
        convert._ffmpeg_has_filter.cache_clear()
        res1 = convert._ffmpeg_has_filter('v360')
        res2 = convert._ffmpeg_has_filter('v360')
        info_after = convert._ffmpeg_has_filter.cache_info()

        self.assertEqual(res1, res2)
        self.assertGreaterEqual(info_after.hits, 1)

    def test_get_video_info_path_normalization(self):
        if not self.has_video:
            self.skipTest("FFmpeg/test video not available")

        convert.get_video_info.cache_clear()

        rel_path = os.path.relpath(self.test_video)
        abs_path = os.path.abspath(self.test_video)

        info1 = convert.get_video_info(rel_path)
        cache_info1 = convert._get_video_info_cached.cache_info()

        info2 = convert.get_video_info(abs_path)
        cache_info2 = convert._get_video_info_cached.cache_info()

        self.assertEqual(info1['width'], 640)
        self.assertEqual(info1['height'], 360)
        self.assertEqual(info1, info2)
        # Second call should be a cache hit because paths normalize to the same abs path
        self.assertEqual(cache_info2.hits, cache_info1.hits + 1)

    def test_get_video_info_cache_clear(self):
        if not self.has_video:
            self.skipTest("FFmpeg/test video not available")

        convert.get_video_info(self.test_video)
        convert.get_video_info.cache_clear()
        cache_info = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache_info.currsize, 0)

    def test_benchmark_encoder_check_speedup(self):
        convert._ffmpeg_has_encoder.cache_clear()

        t0 = time.perf_counter()
        for _ in range(50):
            convert._ffmpeg_has_encoder('non_existent_encoder')
        t_cached = time.perf_counter() - t0

        # With 50 iterations, cached calls should complete almost instantaneously (< 0.05s)
        self.assertLess(t_cached, 0.2)

if __name__ == '__main__':
    unittest.main()
