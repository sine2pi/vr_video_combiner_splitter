import unittest, os, subprocess, time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = 'test_sample.mp4'
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=2:size=640x360:rate=30',
            '-c:v', 'libx264', cls.test_video, '-y'
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info(self):
        convert.get_video_info.cache_clear()
        info = convert.get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertAlmostEqual(info['duration'], 2.0, places=1)

    def test_video_duration(self):
        duration = convert.video_duration(self.test_video)
        self.assertAlmostEqual(duration, 2.0, places=1)

    def test_path_normalization_lru_cache(self):
        convert.get_video_info.cache_clear()
        rel_path = f'./{self.test_video}'
        abs_path = os.path.abspath(self.test_video)

        t0 = time.perf_counter()
        info1 = convert.get_video_info(rel_path)
        t1 = time.perf_counter()
        miss_time = (t1 - t0) * 1000

        t0 = time.perf_counter()
        info2 = convert.get_video_info(abs_path)
        t1 = time.perf_counter()
        hit_time = (t1 - t0) * 1000

        self.assertEqual(info1, info2)
        print(f"\n[BENCHMARK] Metadata Cache Miss: {miss_time:.2f}ms | Cache Hit: {hit_time:.2f}ms")
        self.assertLess(hit_time, miss_time / 5)

    def test_ffmpeg_feature_checks(self):
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

        t0 = time.perf_counter()
        res1 = convert._ffmpeg_has_encoder('libx264')
        t1 = time.perf_counter()
        miss_time = (t1 - t0) * 1000

        t0 = time.perf_counter()
        res2 = convert._ffmpeg_has_encoder('libx264')
        t1 = time.perf_counter()
        hit_time = (t1 - t0) * 1000

        self.assertTrue(res1)
        self.assertEqual(res1, res2)
        print(f"[BENCHMARK] Encoder Check Cache Miss: {miss_time:.2f}ms | Cache Hit: {hit_time:.2f}ms")
        self.assertLess(hit_time, miss_time / 5)

if __name__ == '__main__':
    unittest.main()
