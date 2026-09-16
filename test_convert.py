import unittest
import os, subprocess, shutil, time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = os.path.abspath("test_sample.mp4")
        # Generate 1-second dummy video for testing
        cmd = [
            convert.FFMPEG_BIN, "-y", "-f", "lavfi",
            "-i", "testsrc=duration=1:size=640x360:rate=30",
            "-c:v", "libx264", cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertAlmostEqual(info['duration'], 1.0, places=1)

    def test_video_duration_wrapper(self):
        dur = convert.video_duration(self.test_video)
        self.assertAlmostEqual(dur, 1.0, places=1)

    def test_ffmpeg_has_encoder_caching(self):
        # First call populates LRU cache
        res1 = convert._ffmpeg_has_encoder('libx264')
        t0 = time.perf_counter()
        for _ in range(50):
            res2 = convert._ffmpeg_has_encoder('libx264')
        elapsed = time.perf_counter() - t0
        self.assertEqual(res1, res2)
        # 50 cached calls should complete under 10ms
        self.assertLess(elapsed, 0.01)

    def test_ffmpeg_has_filter_caching(self):
        res1 = convert._ffmpeg_has_filter('v360')
        t0 = time.perf_counter()
        for _ in range(50):
            res2 = convert._ffmpeg_has_filter('v360')
        elapsed = time.perf_counter() - t0
        self.assertEqual(res1, res2)
        self.assertLess(elapsed, 0.01)

    def test_path_normalization_cache_hit(self):
        rel_path = os.path.relpath(self.test_video)
        info1 = convert.get_video_info(self.test_video)

        t0 = time.perf_counter()
        info2 = convert.get_video_info(rel_path)
        elapsed = time.perf_counter() - t0

        self.assertEqual(info1, info2)
        # Second call using relative path should hit LRU cache and execute in under 1ms
        self.assertLess(elapsed, 0.001)

if __name__ == '__main__':
    unittest.main()
