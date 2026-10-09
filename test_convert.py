import unittest
import subprocess
import time
import os
import shutil
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_file = "test_sample.mp4"
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=2:size=1280x720:rate=30',
            '-c:v', 'libx264', cls.test_file
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_returns_correct_metadata(self):
        info = convert.get_video_info(self.test_file)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['duration'], 2.0, places=1)

    def test_legacy_functions_return_correct_metadata(self):
        self.assertEqual(convert.frame_rate(self.test_file), 30.0)
        self.assertEqual(convert.vcodec(self.test_file), 'h264')
        self.assertEqual(convert.vresolution(self.test_file), (1280, 720))
        self.assertAlmostEqual(convert.video_duration(self.test_file), 2.0, places=1)

    def test_video_info_caching_speedup(self):
        # Measure cold lookup (subprocess spawn)
        t0 = time.perf_counter()
        convert.get_video_info(self.test_file)
        t_cold = time.perf_counter() - t0

        # Measure 100 warm cache hits
        t0 = time.perf_counter()
        for _ in range(100):
            convert.get_video_info(self.test_file)
            convert.video_duration(self.test_file)
        t_warm = time.perf_counter() - t0

        # 100 warm cache hits should be orders of magnitude faster than a single cold lookup
        self.assertLess(t_warm, t_cold)

    def test_ffmpeg_encoder_check_caching(self):
        t0 = time.perf_counter()
        r1 = convert._ffmpeg_has_encoder("libx264")
        t_cold = time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(100):
            r2 = convert._ffmpeg_has_encoder("libx264")
        t_warm = time.perf_counter() - t0

        self.assertEqual(r1, r2)
        self.assertLess(t_warm, t_cold)

if __name__ == '__main__':
    unittest.main()
