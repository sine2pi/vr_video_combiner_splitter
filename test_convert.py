import unittest
import time
import os
import subprocess
import convert

class TestConvertPerformanceAndCorrectness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test.mp4"
        if not os.path.exists(cls.test_video):
            # Create a dummy video if it does not exist
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', '-i',
                'testsrc=duration=1:size=1280x720:rate=30',
                '-c:v', 'libx264', cls.test_video
            ], capture_output=True, check=True)

    def test_metadata_correctness(self):
        # Clear cache before starting
        convert.get_video_info.cache_clear()

        # Test correctness of get_video_info
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0)

        # Test correctness of backward compatibility wrappers
        self.assertEqual(convert.frame_rate(self.test_video), 30.0)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (1280, 720))

    def test_performance_improvement(self):
        # Clear cache
        convert.get_video_info.cache_clear()

        # Benchmark first-run metadata extraction (consolidated single ffprobe call)
        start_time = time.time()
        info1 = convert.get_video_info(self.test_video)
        first_run_duration = time.time() - start_time
        print(f"\nConsolidated first run duration (1 ffprobe call): {first_run_duration:.4f} seconds")

        # Benchmark second-run metadata extraction (cached)
        start_time = time.time()
        info2 = convert.get_video_info(self.test_video)
        second_run_duration = time.time() - start_time
        print(f"Cached call duration: {second_run_duration:.6f} seconds")

        # Verify that the cache actually worked and is orders of magnitude faster
        self.assertLess(second_run_duration, first_run_duration)
        self.assertEqual(info1, info2)

        # Estimate the speedup
        speedup_factor = first_run_duration / (second_run_duration if second_run_duration > 0 else 1e-9)
        print(f"Subsequent cached query is {speedup_factor:.1f}x faster!")

if __name__ == '__main__':
    unittest.main()
