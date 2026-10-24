import unittest
import os
import tempfile
import shutil
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.temp_dir, 'test.mp4')
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=1:size=1280x720:rate=30',
            '-c:v', 'libx264', cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_returns_correct_fields(self):
        info = convert.get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)

        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertAlmostEqual(info['fps'], 30.0, delta=0.1)
        self.assertAlmostEqual(info['duration'], 1.0, delta=0.1)

    def test_wrapper_functions(self):
        self.assertEqual(convert.vresolution(self.test_video), (1280, 720))
        self.assertAlmostEqual(convert.frame_rate(self.test_video), 30.0, delta=0.1)
        self.assertAlmostEqual(convert.video_duration(self.test_video), 1.0, delta=0.1)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')

    def test_path_normalization_cache_hit(self):
        info1 = convert.get_video_info(self.test_video)
        # Construct relative path equivalent
        rel_path = os.path.relpath(self.test_video)
        info2 = convert.get_video_info(rel_path)
        info3 = convert.get_video_info(os.path.abspath(self.test_video))

        cache_info = convert.get_video_info.cache_info()
        self.assertEqual(cache_info.hits, 2)
        self.assertEqual(cache_info.misses, 1)

    def test_video_duration_uses_get_video_info_cache(self):
        # Calling video_duration after get_video_info should hit the cache
        convert.get_video_info(self.test_video)
        initial_hits = convert.get_video_info.cache_info().hits
        dur = convert.video_duration(self.test_video)
        self.assertEqual(convert.get_video_info.cache_info().hits, initial_hits + 1)
        self.assertAlmostEqual(dur, 1.0, delta=0.1)

    def test_cache_clear(self):
        convert.get_video_info(self.test_video)
        self.assertGreater(convert.get_video_info.cache_info().currsize, 0)
        convert.get_video_info.cache_clear()
        self.assertEqual(convert.get_video_info.cache_info().currsize, 0)

    def test_ffmpeg_encoder_caching(self):
        has_enc1 = convert._ffmpeg_has_encoder('libx264')
        has_enc2 = convert._ffmpeg_has_encoder('libx264')

        cache_info = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(has_enc1, has_enc2)

    def test_ffmpeg_filter_caching(self):
        has_filt1 = convert._ffmpeg_has_filter('v360')
        has_filt2 = convert._ffmpeg_has_filter('v360')

        cache_info = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(has_filt1, has_filt2)

if __name__ == '__main__':
    unittest.main()
