import unittest
import subprocess
import time
import os
import convert

class TestConvertOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_file = "test_sample.mp4"
        # Generate a dummy test video (1 second, 1280x720 @ 30fps)
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=1:size=1280x720:rate=30',
            '-c:v', 'libx264', cls.test_file
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)

    def setUp(self):
        convert.get_video_info.cache_clear()

    def test_get_video_info_returns_duration(self):
        info = convert.get_video_info(self.test_file)
        self.assertIn('duration', info)
        self.assertAlmostEqual(info['duration'], 1.0, delta=0.1)
        self.assertAlmostEqual(info['fps'], 30.0, delta=0.1)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)

    def test_video_duration_uses_cache(self):
        # First call populates cache
        dur1 = convert.video_duration(self.test_file)
        self.assertAlmostEqual(dur1, 1.0, delta=0.1)

        # Measure cached call time
        t0 = time.perf_counter()
        dur2 = convert.video_duration(self.test_file)
        t1 = time.perf_counter()

        cached_time_ms = (t1 - t0) * 1000
        self.assertEqual(dur1, dur2)
        # Cached call should take less than 1ms
        self.assertLess(cached_time_ms, 1.0)

if __name__ == '__main__':
    unittest.main()
