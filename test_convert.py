import unittest
import os
import time
import subprocess
import shutil
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_sample.mp4"
        if not os.path.exists(cls.test_video):
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=1:size=1280x720:rate=30",
                "-c:v", "libx264", cls.test_video
            ]
            subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            try:
                os.remove(cls.test_video)
            except OSError:
                pass

    def test_get_video_info_and_duration(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)
        self.assertIn('codec', info)

        dur = convert.video_duration(self.test_video)
        self.assertAlmostEqual(dur, 1.0, delta=0.2)

    def test_path_normalization_cache(self):
        if hasattr(convert.get_video_info, 'cache_clear'):
            convert.get_video_info.cache_clear()
        rel_path = self.test_video
        abs_path = os.path.abspath(rel_path)

        info1 = convert.get_video_info(rel_path)

        t0 = time.perf_counter()
        info2 = convert.get_video_info(abs_path)
        t1 = time.perf_counter()

        self.assertEqual(info1['width'], info2['width'])
        self.assertEqual(info1['height'], info2['height'])

    def test_ffmpeg_encoder_filter_caching(self):
        res1 = convert._ffmpeg_has_encoder("hevc_nvenc")
        t1 = time.perf_counter()
        res2 = convert._ffmpeg_has_encoder("hevc_nvenc")
        t2 = time.perf_counter()

        self.assertEqual(res1, res2)

        f1 = convert._ffmpeg_has_filter("v360")
        t4 = time.perf_counter()
        f2 = convert._ffmpeg_has_filter("v360")
        t5 = time.perf_counter()

        self.assertEqual(f1, f2)

if __name__ == '__main__':
    unittest.main()
