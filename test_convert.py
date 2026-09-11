import unittest
import os
import subprocess
import time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_sample.mp4"
        if not os.path.exists(cls.test_video):
            cmd = [
                convert.FFMPEG_BIN, "-y", "-f", "lavfi",
                "-i", "testsrc=duration=2:size=1280x720:rate=30",
                "-c:v", "libx264", cls.test_video
            ]
            subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            try:
                os.remove(cls.test_video)
            except OSError:
                pass

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['duration'], 2.0, places=1)

    def test_video_duration_cached(self):
        duration = convert.video_duration(self.test_video)
        self.assertAlmostEqual(duration, 2.0, places=1)

    def test_path_normalization_cache_hit(self):
        convert.get_video_info.cache_clear()

        # Cold call
        t0 = time.perf_counter()
        info1 = convert.get_video_info(self.test_video)
        t_cold = time.perf_counter() - t0

        # Equivalent path strings (relative vs normalized)
        rel_path = os.path.join(".", self.test_video)
        t0 = time.perf_counter()
        info2 = convert.get_video_info(rel_path)
        t_warm = time.perf_counter() - t0

        self.assertEqual(info1, info2)
        # Warm call should be drastically faster (< 1ms vs ~20ms)
        self.assertLess(t_warm, max(t_cold / 5, 0.005))

    def test_ffmpeg_has_encoder_caching(self):
        convert._ffmpeg_has_encoder.cache_clear()

        t0 = time.perf_counter()
        res1 = convert._ffmpeg_has_encoder("libx264")
        t_cold = time.perf_counter() - t0

        t0 = time.perf_counter()
        res2 = convert._ffmpeg_has_encoder("libx264")
        t_warm = time.perf_counter() - t0

        self.assertEqual(res1, res2)
        self.assertLess(t_warm, 0.001)

    def test_ffmpeg_has_filter_caching(self):
        convert._ffmpeg_has_filter.cache_clear()

        t0 = time.perf_counter()
        res1 = convert._ffmpeg_has_filter("v360")
        t_cold = time.perf_counter() - t0

        t0 = time.perf_counter()
        res2 = convert._ffmpeg_has_filter("v360")
        t_warm = time.perf_counter() - t0

        self.assertEqual(res1, res2)
        self.assertLess(t_warm, 0.001)

if __name__ == '__main__':
    unittest.main()
