import unittest
import os
import subprocess
import time
import convert

class TestConvertOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = os.path.abspath("test_dummy.mp4")
        # Create a tiny 1-second dummy MP4 video using ffmpeg
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=1:size=640x480:rate=30",
            "-c:v", "libx264", cls.test_video
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def setUp(self):
        convert.get_video_info.cache_clear()

    def test_metadata_extraction_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 480)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')

    def test_lru_cache_hit_on_path_variants(self):
        rel_path1 = "test_dummy.mp4"
        rel_path2 = "./test_dummy.mp4"
        abs_path = self.test_video

        # First call populates cache
        convert.get_video_info(rel_path1)
        info1 = convert.get_video_info.cache_info()
        self.assertEqual(info1.hits, 0)
        self.assertEqual(info1.misses, 1)

        # Second call with different path representation should HIT cache
        convert.get_video_info(rel_path2)
        info2 = convert.get_video_info.cache_info()
        self.assertEqual(info2.hits, 1)

        # Third call with absolute path should HIT cache
        convert.get_video_info(abs_path)
        info3 = convert.get_video_info.cache_info()
        self.assertEqual(info3.hits, 2)

    def test_performance_speedup(self):
        rel_path1 = "test_dummy.mp4"
        rel_path2 = "./test_dummy.mp4"
        abs_path = self.test_video

        convert.get_video_info.cache_clear()

        t0 = time.perf_counter()
        convert.get_video_info(rel_path1)
        t_uncached = time.perf_counter() - t0

        t0 = time.perf_counter()
        convert.get_video_info(rel_path2)
        convert.get_video_info(abs_path)
        t_cached = time.perf_counter() - t0

        # Cached lookups should be orders of magnitude faster (no subprocess spawned)
        self.assertLess(t_cached, t_uncached)

if __name__ == "__main__":
    unittest.main()
