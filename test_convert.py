import unittest
import os
import subprocess
import shutil
import tempfile
import time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.temp_dir, "sample.mp4")
        ffmpeg_bin = shutil.which('ffmpeg') or 'ffmpeg'
        cmd = [
            ffmpeg_bin, "-y", "-f", "lavfi",
            "-i", "testsrc=duration=2:size=640x360:rate=30",
            "-c:v", "libx264", cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_video_info_returns_expected_keys(self):
        info = convert.get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertAlmostEqual(info['fps'], 30.0, delta=0.5)
        self.assertAlmostEqual(info['duration'], 2.0, delta=0.2)

    def test_video_duration(self):
        dur = convert.video_duration(self.test_video)
        self.assertAlmostEqual(dur, 2.0, delta=0.2)

    def test_ffmpeg_has_encoder_and_filter(self):
        self.assertTrue(convert._ffmpeg_has_encoder("libx264"))
        self.assertTrue(convert._ffmpeg_has_filter("scale"))

    def test_lru_cache_performance(self):
        # Warm cache
        convert._ffmpeg_has_encoder("libx264")
        t0 = time.perf_counter()
        for _ in range(100):
            convert._ffmpeg_has_encoder("libx264")
        t1 = time.perf_counter()
        # 100 cached calls should complete in under 5ms
        self.assertLess(t1 - t0, 0.005)

    def test_path_normalization_cache_hit(self):
        convert.get_video_info.cache_clear()
        info1 = convert.get_video_info(self.test_video)
        rel_path = os.path.relpath(self.test_video)
        info2 = convert.get_video_info(rel_path)
        self.assertEqual(info1, info2)
        # Should have 1 hit and 1 miss
        cache_info = convert.get_video_info.cache_info()
        self.assertEqual(cache_info.hits, 1)

if __name__ == '__main__':
    unittest.main()
