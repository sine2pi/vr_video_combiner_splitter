import unittest
import os
import subprocess
import time
import convert

class TestConvertOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = os.path.abspath("test_sample.mp4")
        # Generate dummy 1-second video with ffmpeg for testing
        cmd = [
            "ffmpeg", "-hide_banner", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=1:size=1280x720:rate=30",
            "-c:v", "libx264", cls.test_video
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)
        self.assertIn(info['codec'], ['h264', 'avc1'])

    def test_path_normalization_cache_hit(self):
        rel_path = "test_sample.mp4"
        alt_rel_path = "./test_sample.mp4"
        abs_path = os.path.abspath(rel_path)

        # Clear cache before measuring
        convert._get_video_info_cached.cache_clear()

        t0 = time.perf_counter()
        info1 = convert.get_video_info(rel_path)
        t1 = time.perf_counter()

        info2 = convert.get_video_info(alt_rel_path)
        t2 = time.perf_counter()

        info3 = convert.get_video_info(abs_path)
        t3 = time.perf_counter()

        first_call_ms = (t1 - t0) * 1000
        second_call_ms = (t2 - t1) * 1000
        third_call_ms = (t3 - t2) * 1000

        self.assertEqual(info1, info2)
        self.assertEqual(info1, info3)

        # Second and third calls should be cached (< 1ms vs ~70ms ffprobe execution)
        self.assertLess(second_call_ms, 5.0)
        self.assertLess(third_call_ms, 5.0)

        cache_info = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache_info.hits, 2)
        self.assertEqual(cache_info.misses, 1)

if __name__ == "__main__":
    unittest.main()
