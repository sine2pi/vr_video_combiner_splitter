import unittest
import os
import time
import subprocess
import shutil
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_sample.mp4"
        cmd = [
            shutil.which('ffmpeg') or 'ffmpeg',
            '-f', 'lavfi',
            '-i', 'testsrc=duration=2:size=1280x720:rate=30',
            '-c:v', 'libx264',
            '-y',
            cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertAlmostEqual(info['duration'], 2.0, places=1)

    def test_video_duration_wrapper(self):
        duration = convert.video_duration(self.test_video)
        self.assertAlmostEqual(duration, 2.0, places=1)

    def test_lru_cache_hit(self):
        convert.get_video_info.cache_clear()

        t0 = time.perf_counter()
        info1 = convert.get_video_info(self.test_video)
        t_uncached = time.perf_counter() - t0

        t0 = time.perf_counter()
        info2 = convert.get_video_info(self.test_video)
        t_cached = time.perf_counter() - t0

        self.assertEqual(info1, info2)
        # Cached hit should be dramatically faster (at least 10x faster)
        self.assertLess(t_cached, t_uncached / 10)

    def test_path_normalization_cache_hit(self):
        convert.get_video_info.cache_clear()
        rel_path = self.test_video
        abs_path = os.path.abspath(rel_path)

        info1 = convert.get_video_info(rel_path)
        cache_info_1 = convert.get_video_info.cache_info()

        info2 = convert.get_video_info(abs_path)
        cache_info_2 = convert.get_video_info.cache_info()

        self.assertEqual(info1, info2)
        # Verify hit count increased by 1 for equivalent path
        self.assertEqual(cache_info_2.hits, cache_info_1.hits + 1)

    def test_ffmpeg_encoder_and_filter_cache(self):
        convert._ffmpeg_has_encoder.cache_clear()

        t0 = time.perf_counter()
        has_libx264_1 = convert._ffmpeg_has_encoder("libx264")
        t_uncached = time.perf_counter() - t0

        t0 = time.perf_counter()
        has_libx264_2 = convert._ffmpeg_has_encoder("libx264")
        t_cached = time.perf_counter() - t0

        self.assertEqual(has_libx264_1, has_libx264_2)
        self.assertLess(t_cached, t_uncached / 10)

if __name__ == "__main__":
    unittest.main()
