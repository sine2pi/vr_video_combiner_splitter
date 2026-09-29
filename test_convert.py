import unittest
import os
import subprocess
import time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_opt_sample.mp4"
        # Generate a test video using ffmpeg
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=2:size=1280x720:rate=30',
            '-c:v', 'libx264', cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_ffmpeg_has_encoder_cached(self):
        convert._ffmpeg_has_encoder.cache_clear()

        t0 = time.perf_counter()
        res1 = convert._ffmpeg_has_encoder('libx264')
        t1 = time.perf_counter()
        uncached_time = (t1 - t0) * 1000

        t0 = time.perf_counter()
        res2 = convert._ffmpeg_has_encoder('libx264')
        t1 = time.perf_counter()
        cached_time = (t1 - t0) * 1000

        self.assertEqual(res1, res2)
        print(f"\n[_ffmpeg_has_encoder] Uncached: {uncached_time:.2f}ms | Cached: {cached_time:.4f}ms")
        self.assertLess(cached_time, uncached_time)

    def test_ffmpeg_has_filter_cached(self):
        convert._ffmpeg_has_filter.cache_clear()

        t0 = time.perf_counter()
        res1 = convert._ffmpeg_has_filter('v360')
        t1 = time.perf_counter()
        uncached_time = (t1 - t0) * 1000

        t0 = time.perf_counter()
        res2 = convert._ffmpeg_has_filter('v360')
        t1 = time.perf_counter()
        cached_time = (t1 - t0) * 1000

        self.assertEqual(res1, res2)
        print(f"[_ffmpeg_has_filter] Uncached: {uncached_time:.2f}ms | Cached: {cached_time:.4f}ms")
        self.assertLess(cached_time, uncached_time)

    def test_get_video_info_and_duration_cached(self):
        convert.get_video_info.cache_clear()

        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertAlmostEqual(info['duration'], 2.0, delta=0.2)

        # Ensure video_duration uses cached info
        t0 = time.perf_counter()
        dur = convert.video_duration(self.test_video)
        t1 = time.perf_counter()
        cached_dur_time = (t1 - t0) * 1000

        self.assertAlmostEqual(dur, 2.0, delta=0.2)
        print(f"[video_duration] Cached retrieval time: {cached_dur_time:.4f}ms")
        self.assertLess(cached_dur_time, 1.0)

if __name__ == '__main__':
    unittest.main()
