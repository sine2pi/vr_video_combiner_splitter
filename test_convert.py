import unittest
import os
import subprocess
import time
import convert

class TestConvertMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = os.path.abspath("test_sample.mp4")
        if not os.path.exists(cls.test_video):
            cmd = [
                "ffmpeg", "-hide_banner", "-y",
                "-f", "lavfi", "-i", "testsrc=duration=1:size=1280x720:rate=30",
                "-c:v", "libx264", cls.test_video
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            try:
                os.remove(cls.test_video)
            except Exception:
                pass

    def setUp(self):
        convert.get_video_info.cache_clear()

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)

    def test_helper_wrappers(self):
        self.assertEqual(convert.frame_rate(self.test_video), 30.0)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (1280, 720))

    def test_path_normalization_cache_hit(self):
        p1 = "test_sample.mp4"
        p2 = "./test_sample.mp4"
        p3 = os.path.abspath("test_sample.mp4")

        # First call populates cache
        t0 = time.perf_counter()
        info1 = convert.get_video_info(p1)
        t_first = (time.perf_counter() - t0) * 1000

        # Subsequent calls with equivalent path strings should hit the LRU cache
        t0 = time.perf_counter()
        info2 = convert.get_video_info(p2)
        t_second = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        info3 = convert.get_video_info(p3)
        t_third = (time.perf_counter() - t0) * 1000

        self.assertEqual(info1, info2)
        self.assertEqual(info2, info3)

        cache_info = convert.get_video_info.cache_info()
        self.assertEqual(cache_info.hits, 2)
        self.assertEqual(cache_info.misses, 1)

        print(f"\n[Benchmark] Initial ffprobe call: {t_first:.2f}ms | Relative path cache hit: {t_second:.4f}ms | Absolute path cache hit: {t_third:.4f}ms")

if __name__ == '__main__':
    unittest.main()
