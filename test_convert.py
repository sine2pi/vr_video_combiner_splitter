import unittest, subprocess, os, time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_sample.mp4"
        cmd = [
            convert.FFMPEG_BIN, "-y",
            "-f", "lavfi", "-i", "testsrc=duration=2.5:size=640x360:rate=30",
            "-c:v", "libx264",
            cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_returns_duration(self):
        info = convert.get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)
        self.assertAlmostEqual(info['duration'], 2.5, delta=0.5)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)

    def test_video_duration_matches_info(self):
        dur = convert.video_duration(self.test_video)
        info = convert.get_video_info(self.test_video)
        self.assertEqual(dur, info['duration'])

    def test_cache_clear_forwarding(self):
        convert.get_video_info(self.test_video)
        info_before = convert.get_video_info.cache_info()
        self.assertGreaterEqual(info_before.hits + info_before.misses, 1)
        convert.get_video_info.cache_clear()
        info_after = convert.get_video_info.cache_info()
        self.assertEqual(info_after.hits, 0)
        self.assertEqual(info_after.misses, 0)

    def test_ffmpeg_has_encoder_caching(self):
        res1 = convert._ffmpeg_has_encoder("libx264")
        res2 = convert._ffmpeg_has_encoder("libx264")
        self.assertEqual(res1, res2)
        cache_info = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(cache_info.hits, 1)

    def test_ffmpeg_has_filter_caching(self):
        res1 = convert._ffmpeg_has_filter("v360")
        res2 = convert._ffmpeg_has_filter("v360")
        self.assertEqual(res1, res2)
        cache_info = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(cache_info.hits, 1)

if __name__ == "__main__":
    unittest.main()
