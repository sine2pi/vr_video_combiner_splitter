import os
import time
import unittest
import subprocess
import convert

class TestConvertMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test.mp4"
        # Generate dummy video
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            "testsrc=duration=1:size=1280x720:rate=30",
            "-c:v", "libx264", cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            try:
                os.remove(cls.test_video)
            except Exception:
                pass

    def test_get_video_info_correctness(self):
        # Verify get_video_info returns expected data
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['codec'], 'h264')
        self.assertEqual(info['fps'], 30.0)

    def test_legacy_functions(self):
        # Verify compatibility wrappers
        self.assertEqual(convert.frame_rate(self.test_video), 30.0)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (1280, 720))

    def test_caching_performance(self):
        # Clear cache first to measure cold run
        convert.get_video_info.cache_clear()

        # Cold run
        start_cold = time.perf_counter()
        info1 = convert.get_video_info(self.test_video)
        end_cold = time.perf_counter()
        cold_duration = (end_cold - start_cold) * 1000  # in ms

        # Warm run (cached)
        start_warm = time.perf_counter()
        info2 = convert.get_video_info(self.test_video)
        end_warm = time.perf_counter()
        warm_duration = (end_warm - start_warm) * 1000  # in ms

        print(f"\n[BENCHMARK] Cold metadata retrieval: {cold_duration:.4f} ms")
        print(f"[BENCHMARK] Warm metadata retrieval (cached): {warm_duration:.4f} ms")

        # Subsequent requests must be virtually instantaneous
        self.assertLess(warm_duration, 1.0, "Cached lookup should take less than 1ms")
        self.assertEqual(info1, info2)

if __name__ == "__main__":
    unittest.main()
