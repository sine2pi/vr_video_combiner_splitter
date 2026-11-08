import unittest
import os
import tempfile
import subprocess
import time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a dummy test video using ffmpeg
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_video = os.path.join(cls.temp_dir.name, 'test.mp4')
        try:
            cmd = [
                convert.FFMPEG_BIN,
                '-f', 'lavfi', '-i', 'testsrc=duration=1:size=640x360:rate=30',
                '-c:v', 'libx264', '-y', cls.test_video
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            cls.has_video = True
        except Exception:
            cls.has_video = False

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_get_video_info_returns_duration(self):
        if not self.has_video:
            self.skipTest('FFmpeg/test video not available')

        convert.get_video_info.cache_clear()
        info = convert.get_video_info(self.test_video)

        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['duration'], 1.0, places=1)

    def test_video_duration_uses_get_video_info_cache(self):
        if not self.has_video:
            self.skipTest('FFmpeg/test video not available')

        convert.get_video_info.cache_clear()
        dur1 = convert.video_duration(self.test_video)
        cache_info1 = convert.get_video_info.cache_info()

        dur2 = convert.video_duration(self.test_video)
        cache_info2 = convert.get_video_info.cache_info()

        self.assertAlmostEqual(dur1, 1.0, places=1)
        self.assertEqual(dur1, dur2)
        # Second call should hit the cache without running ffprobe
        self.assertEqual(cache_info2.hits, cache_info1.hits + 1)

    def test_get_video_info_path_normalization(self):
        if not self.has_video:
            self.skipTest('FFmpeg/test video not available')

        convert.get_video_info.cache_clear()

        rel_path = os.path.relpath(self.test_video)
        abs_path = os.path.abspath(self.test_video)

        info1 = convert.get_video_info(rel_path)
        cache_info1 = convert.get_video_info.cache_info()

        info2 = convert.get_video_info(abs_path)
        cache_info2 = convert.get_video_info.cache_info()

        self.assertEqual(info1, info2)
        # Second call with different path format should hit the cache due to normalization
        self.assertEqual(cache_info2.hits, cache_info1.hits + 1)

    def test_backward_compatibility_helpers(self):
        if not self.has_video:
            self.skipTest('FFmpeg/test video not available')

        convert.get_video_info.cache_clear()
        self.assertEqual(convert.frame_rate(self.test_video), 30.0)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (640, 360))
        self.assertAlmostEqual(convert.video_duration(self.test_video), 1.0, places=1)

    def test_cache_clear(self):
        if not self.has_video:
            self.skipTest('FFmpeg/test video not available')

        convert.get_video_info(self.test_video)
        self.assertGreaterEqual(convert.get_video_info.cache_info().currsize, 1)
        convert.get_video_info.cache_clear()
        self.assertEqual(convert.get_video_info.cache_info().currsize, 0)

if __name__ == '__main__':
    unittest.main()
