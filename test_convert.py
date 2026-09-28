import unittest
import os
import time
import tempfile
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.video_path = os.path.join(cls.temp_dir.name, "test_sample.mp4")
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=2:size=640x360:rate=30',
            '-c:v', 'libx264',
            cls.video_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_and_wrappers(self):
        info = convert.get_video_info(self.video_path)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertAlmostEqual(info['duration'], 2.0, places=1)

        self.assertAlmostEqual(convert.frame_rate(self.video_path), 30.0, places=1)
        self.assertEqual(convert.vcodec(self.video_path), 'h264')
        self.assertEqual(convert.vresolution(self.video_path), (640, 360))
        self.assertAlmostEqual(convert.video_duration(self.video_path), 2.0, places=1)

    def test_path_normalization_cache_hit(self):
        rel_path = os.path.relpath(self.video_path)
        abs_path = os.path.abspath(self.video_path)

        info1 = convert.get_video_info(rel_path)
        cache_info_before = convert._get_video_info_cached.cache_info()

        info2 = convert.get_video_info(abs_path)
        cache_info_after = convert._get_video_info_cached.cache_info()

        self.assertEqual(info1, info2)
        self.assertEqual(cache_info_after.hits, cache_info_before.hits + 1)

    def test_ffmpeg_encoder_and_filter_cache(self):
        res1 = convert._ffmpeg_has_encoder('libx264')
        info_before = convert._ffmpeg_has_encoder.cache_info()
        res2 = convert._ffmpeg_has_encoder('libx264')
        info_after = convert._ffmpeg_has_encoder.cache_info()

        self.assertEqual(res1, res2)
        self.assertEqual(info_after.hits, info_before.hits + 1)

        res_f1 = convert._ffmpeg_has_filter('scale')
        info_f_before = convert._ffmpeg_has_filter.cache_info()
        res_f2 = convert._ffmpeg_has_filter('scale')
        info_f_after = convert._ffmpeg_has_filter.cache_info()

        self.assertEqual(res_f1, res_f2)
        self.assertEqual(info_f_after.hits, info_f_before.hits + 1)

    def test_performance_benchmark(self):
        t0 = time.perf_counter()
        dur_cold = convert.video_duration(self.video_path)
        t_cold = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        dur_cached = convert.video_duration(self.video_path)
        t_cached = (time.perf_counter() - t0) * 1000

        self.assertEqual(dur_cold, dur_cached)
        print(f"\n[BENCHMARK] video_duration Cold: {t_cold:.3f} ms | Cached: {t_cached:.3f} ms")
        self.assertLess(t_cached, t_cold)

if __name__ == '__main__':
    unittest.main()
