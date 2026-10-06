import unittest
import os
import time
import tempfile
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary test video using ffmpeg
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.video_path = os.path.join(cls.temp_dir.name, "test_video.mp4")
        cmd = [
            convert.FFMPEG_BIN,
            "-y",
            "-f", "lavfi",
            "-i", "testsrc=duration=2:size=640x480:rate=30",
            "-c:v", "libx264",
            cls.video_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_get_video_info(self):
        convert.get_video_info.cache_clear()
        info = convert.get_video_info(self.video_path)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 480)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertAlmostEqual(info['duration'], 2.0, places=1)

    def test_video_duration_uses_cache(self):
        convert.get_video_info.cache_clear()
        dur1 = convert.video_duration(self.video_path)
        cache_info1 = convert.get_video_info.cache_info()
        dur2 = convert.video_duration(self.video_path)
        cache_info2 = convert.get_video_info.cache_info()

        self.assertAlmostEqual(dur1, 2.0, places=1)
        self.assertEqual(dur1, dur2)
        self.assertGreater(cache_info2.hits, cache_info1.hits)

    def test_ffmpeg_has_encoder_cached(self):
        convert._ffmpeg_has_encoder.cache_clear()

        t0 = time.perf_counter()
        has_libx264_1 = convert._ffmpeg_has_encoder("libx264")
        t1 = time.perf_counter()

        t2 = time.perf_counter()
        has_libx264_2 = convert._ffmpeg_has_encoder("libx264")
        t3 = time.perf_counter()

        self.assertTrue(has_libx264_1)
        self.assertEqual(has_libx264_1, has_libx264_2)
        # Cached hit should be significantly faster (under 1ms)
        self.assertLess((t3 - t2), (t1 - t0))

    def test_ffmpeg_has_filter_cached(self):
        convert._ffmpeg_has_filter.cache_clear()

        t0 = time.perf_counter()
        has_v360_1 = convert._ffmpeg_has_filter("v360")
        t1 = time.perf_counter()

        t2 = time.perf_counter()
        has_v360_2 = convert._ffmpeg_has_filter("v360")
        t3 = time.perf_counter()

        self.assertEqual(has_v360_1, has_v360_2)
        self.assertLess((t3 - t2), (t1 - t0))

if __name__ == "__main__":
    unittest.main()
