import unittest
import os
import tempfile
import time
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_video = os.path.join(cls.temp_dir.name, "test_sample.mp4")
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=2:size=1280x720:rate=30',
            '-c:v', 'libx264',
            cls.test_video
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_get_video_info(self):
        convert.get_video_info.cache_clear()
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertAlmostEqual(info['duration'], 2.0, delta=0.2)
        self.assertIn(info['codec'], ['h264', 'avc1'])

    def test_legacy_wrappers(self):
        self.assertEqual(convert.frame_rate(self.test_video), 30.0)
        self.assertEqual(convert.vresolution(self.test_video), (1280, 720))
        self.assertAlmostEqual(convert.video_duration(self.test_video), 2.0, delta=0.2)

    def test_ffmpeg_checks_cached(self):
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

        t0 = time.perf_counter()
        res1 = convert._ffmpeg_has_encoder("libx264")
        t1 = time.perf_counter()
        cold_time = t1 - t0

        t0 = time.perf_counter()
        res2 = convert._ffmpeg_has_encoder("libx264")
        t1 = time.perf_counter()
        cached_time = t1 - t0

        self.assertEqual(res1, res2)
        self.assertLess(cached_time, cold_time)

if __name__ == "__main__":
    unittest.main()
