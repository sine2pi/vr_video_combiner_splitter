import unittest
import os
import time
import subprocess
import convert

class TestConvertOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_sample_video.mp4"
        if not os.path.exists(cls.test_video):
            cmd = [
                convert.FFMPEG_BIN, "-y", "-f", "lavfi",
                "-i", "testsrc=duration=2:size=640x360:rate=30",
                "-c:v", "libx264", cls.test_video
            ]
            subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info_returns_duration(self):
        info = convert.get_video_info(self.test_video)
        self.assertIn('duration', info)
        self.assertAlmostEqual(info['duration'], 2.0, delta=0.5)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)

    def test_video_duration_matches_get_video_info(self):
        info_dur = convert.get_video_info(self.test_video)['duration']
        func_dur = convert.video_duration(self.test_video)
        self.assertEqual(info_dur, func_dur)

    def test_lru_cache_performance(self):
        convert.get_video_info.cache_clear()

        t0 = time.perf_counter()
        dur1 = convert.video_duration(self.test_video)
        t1 = time.perf_counter()
        first_call_time = (t1 - t0) * 1000

        t0 = time.perf_counter()
        dur2 = convert.video_duration(self.test_video)
        t1 = time.perf_counter()
        second_call_time = (t1 - t0) * 1000

        self.assertEqual(dur1, dur2)
        # Cached hit should be at least 10x faster
        self.assertLess(second_call_time, first_call_time / 10)

if __name__ == "__main__":
    unittest.main()
