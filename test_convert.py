import unittest
import os
import subprocess
import tempfile
import functools
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_video = os.path.join(cls.temp_dir.name, "test_sample.mp4")
        # Generate 1-second 30fps sample video using ffmpeg
        cmd = [
            convert.FFMPEG_BIN, "-y",
            "-f", "lavfi", "-i", "testsrc=duration=1:size=640x360:rate=30",
            "-c:v", "libx264",
            cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info(self):
        info = convert.get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertAlmostEqual(info['fps'], 30.0, delta=0.5)
        self.assertAlmostEqual(info['duration'], 1.0, delta=0.5)

    def test_helper_functions(self):
        self.assertAlmostEqual(convert.frame_rate(self.test_video), 30.0, delta=0.5)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (640, 360))
        self.assertAlmostEqual(convert.video_duration(self.test_video), 1.0, delta=0.5)

    def test_cache_and_path_normalization(self):
        info1 = convert.get_video_info(self.test_video)
        info_cache1 = convert.get_video_info.cache_info()

        # Call with relative path / normalized path pointing to same file
        rel_path = os.path.relpath(self.test_video)
        info2 = convert.get_video_info(rel_path)
        info_cache2 = convert.get_video_info.cache_info()

        self.assertEqual(info1, info2)
        self.assertEqual(info_cache2.hits, info_cache1.hits + 1)

    def test_cache_clear(self):
        _ = convert.get_video_info(self.test_video)
        self.assertGreater(convert.get_video_info.cache_info().currsize, 0)
        convert.get_video_info.cache_clear()
        self.assertEqual(convert.get_video_info.cache_info().currsize, 0)

    def test_ffmpeg_feature_checks_cached(self):
        has_h264_1 = convert._ffmpeg_has_encoder("libx264")
        cache_info1 = convert._ffmpeg_has_encoder.cache_info()

        has_h264_2 = convert._ffmpeg_has_encoder("libx264")
        cache_info2 = convert._ffmpeg_has_encoder.cache_info()

        self.assertEqual(has_h264_1, has_h264_2)
        self.assertEqual(cache_info2.hits, cache_info1.hits + 1)

if __name__ == "__main__":
    unittest.main()
