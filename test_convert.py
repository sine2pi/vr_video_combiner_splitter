import unittest
import os
import subprocess
import time
import convert

class TestConvertMetaData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "sample_test.mp4"
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", "testsrc=duration=1:size=1280x720:rate=30",
            "-c:v", "libx264", cls.test_video
        ]
        subprocess.run(cmd, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')

    def test_legacy_wrappers(self):
        self.assertEqual(convert.frame_rate(self.test_video), 30.0)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (1280, 720))

    def test_lru_cache_path_normalization(self):
        # Clear cache first if needed
        convert._get_video_info_cached.cache_clear()

        path_rel = self.test_video
        path_dot = os.path.join(".", self.test_video)
        path_abs = os.path.abspath(self.test_video)

        # First call populates cache
        t0 = time.perf_counter()
        info1 = convert.get_video_info(path_rel)
        t1 = time.perf_counter()
        time_uncached = t1 - t0

        # Second call with ./ relative path
        t2 = time.perf_counter()
        info2 = convert.get_video_info(path_dot)
        t3 = time.perf_counter()
        time_cached_dot = t3 - t2

        # Third call with absolute path
        t4 = time.perf_counter()
        info3 = convert.get_video_info(path_abs)
        t5 = time.perf_counter()
        time_cached_abs = t5 - t4

        self.assertEqual(info1, info2)
        self.assertEqual(info1, info3)

        # Cache hits should be orders of magnitude faster (< 1ms vs ~50-300ms)
        self.assertLess(time_cached_dot, 0.005)
        self.assertLess(time_cached_abs, 0.005)
        print(f"\n[Benchmark] Uncached ffprobe: {time_uncached*1000:.2f}ms")
        print(f"[Benchmark] Cached (./ path): {time_cached_dot*1000:.4f}ms")
        print(f"[Benchmark] Cached (abs path): {time_cached_abs*1000:.4f}ms")

if __name__ == '__main__':
    unittest.main()
