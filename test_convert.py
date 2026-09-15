import unittest
import os
import subprocess
import tempfile
import time
import convert


class TestConvertOptimizations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.video_path = os.path.join(cls.temp_dir.name, "test_sample.mp4")
        # Generate 1-second sample video using ffmpeg
        cmd = [
            convert.FFMPEG_BIN,
            "-y",
            "-f", "lavfi",
            "-i", "testsrc=duration=1:size=640x360:rate=30",
            "-c:v", "libx264",
            cls.video_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_get_video_info(self):
        info = convert.get_video_info(self.video_path)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertAlmostEqual(info['fps'], 30.0, delta=0.5)
        self.assertGreater(info['duration'], 0.0)

    def test_wrappers(self):
        fps = convert.frame_rate(self.video_path)
        codec = convert.vcodec(self.video_path)
        w, h = convert.vresolution(self.video_path)
        duration = convert.video_duration(self.video_path)

        info = convert.get_video_info(self.video_path)
        self.assertEqual(fps, info['fps'])
        self.assertEqual(codec, info['codec'])
        self.assertEqual((w, h), (info['width'], info['height']))
        self.assertEqual(duration, info['duration'])

    def test_path_normalization_caching(self):
        convert._get_video_info_cached.cache_clear()

        abs_path = os.path.abspath(self.video_path)
        rel_path = os.path.relpath(abs_path)

        info1 = convert.get_video_info(abs_path)
        cache_info_after_first = convert._get_video_info_cached.cache_info()

        info2 = convert.get_video_info(rel_path)
        cache_info_after_second = convert._get_video_info_cached.cache_info()

        self.assertEqual(info1, info2)
        self.assertEqual(cache_info_after_first.hits + 1, cache_info_after_second.hits)

    def test_ffmpeg_feature_checks_caching(self):
        convert._ffmpeg_has_encoder.cache_clear()

        t0 = time.perf_counter()
        has_libx264 = convert._ffmpeg_has_encoder("libx264")
        t1 = time.perf_counter()

        has_libx264_cached = convert._ffmpeg_has_encoder("libx264")
        t2 = time.perf_counter()

        self.assertEqual(has_libx264, has_libx264_cached)
        first_call_time = t1 - t0
        second_call_time = t2 - t1

        # Cached call should be significantly faster (microseconds vs milliseconds)
        self.assertLess(second_call_time, first_call_time)


if __name__ == '__main__':
    unittest.main()
