import unittest
import os
import subprocess
import time
import convert

class TestConvertOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_sample_vid.mp4"
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi', '-i',
            'testsrc=duration=3:size=1280x720:rate=30',
            '-c:v', 'libx264', cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def setUp(self):
        convert.get_video_info.cache_clear()

    def test_get_video_info_returns_duration_and_metadata(self):
        info = convert.get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)

        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertAlmostEqual(info['duration'], 3.0, delta=0.5)

    def test_video_duration_uses_get_video_info_cache(self):
        # First call populates cache
        t0 = time.perf_counter()
        dur = convert.video_duration(self.test_video)
        t1 = time.perf_counter()
        first_call_time = (t1 - t0) * 1000

        # Second call should be near-instantaneous (< 1ms) because of LRU cache
        t2 = time.perf_counter()
        dur_cached = convert.video_duration(self.test_video)
        t3 = time.perf_counter()
        second_call_time = (t3 - t2) * 1000

        self.assertAlmostEqual(dur, dur_cached)
        self.assertLess(second_call_time, 1.0)
        print(f"\n[Benchmark] First call: {first_call_time:.2f}ms, Cached call: {second_call_time:.4f}ms")

if __name__ == '__main__':
    unittest.main()
