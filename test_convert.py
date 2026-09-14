import unittest
import os
import time
import shutil
import tempfile
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.temp_dir, "test_sample.mp4")
        # Generate dummy 1-second video with ffmpeg
        cmd = [
            convert.FFMPEG_BIN,
            "-y",
            "-f", "lavfi",
            "-i", "testsrc=duration=1:size=640x360:rate=30",
            "-c:v", "libx264",
            cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_and_duration(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['duration'], 1.0, delta=0.2)

        duration = convert.video_duration(self.test_video)
        self.assertAlmostEqual(duration, 1.0, delta=0.2)

    def test_ffmpeg_has_encoder_and_filter(self):
        res_enc = convert._ffmpeg_has_encoder("libx264")
        self.assertTrue(res_enc)

        res_filt = convert._ffmpeg_has_filter("v360")
        self.assertIsInstance(res_filt, bool)

    def test_performance_benchmark(self):
        # Measure uncached vs cached execution for get_video_info & video_duration
        t0 = time.perf_counter()
        info1 = convert.get_video_info(self.test_video)
        t_first = time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(100):
            _ = convert.get_video_info(self.test_video)
            _ = convert.video_duration(self.test_video)
        t_cached = time.perf_counter() - t0

        print(f"\n[Benchmark] First get_video_info: {t_first * 1000:.2f} ms")
        print(f"[Benchmark] 100 cached get_video_info & video_duration calls: {t_cached * 1000:.2f} ms")

        # 100 cached calls should complete faster than 1 uncached call
        self.assertLess(t_cached, t_first)

        # Measure caching speedup on _ffmpeg_has_encoder
        t0 = time.perf_counter()
        _ = convert._ffmpeg_has_encoder("libx264")
        t_enc_first = time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(100):
            _ = convert._ffmpeg_has_encoder("libx264")
        t_enc_cached = time.perf_counter() - t0

        print(f"[Benchmark] First _ffmpeg_has_encoder: {t_enc_first * 1000:.2f} ms")
        print(f"[Benchmark] 100 cached _ffmpeg_has_encoder calls: {t_enc_cached * 1000:.2f} ms")
        self.assertLess(t_enc_cached, t_enc_first)

if __name__ == "__main__":
    unittest.main()
