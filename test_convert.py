import unittest
import os
import shutil
import tempfile
import subprocess
import time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.temp_dir, "test_sample.mp4")
        # Generate a test video using ffmpeg lavfi
        cmd = [
            convert.FFMPEG_BIN, "-y", "-f", "lavfi",
            "-i", "testsrc=duration=1:size=640x360:rate=30",
            "-c:v", "libx264", cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_and_wrappers(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertAlmostEqual(info['duration'], 1.0, delta=0.2)

        self.assertEqual(convert.frame_rate(self.test_video), 30.0)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (640, 360))
        self.assertAlmostEqual(convert.video_duration(self.test_video), 1.0, delta=0.2)

    def test_lru_cache_path_normalization(self):
        rel_path = os.path.relpath(self.test_video)
        abs_path = os.path.abspath(self.test_video)

        info1 = convert.get_video_info(rel_path)
        cache_info1 = convert.get_video_info.cache_info()
        self.assertEqual(cache_info1.hits, 0)
        self.assertEqual(cache_info1.misses, 1)

        info2 = convert.get_video_info(abs_path)
        cache_info2 = convert.get_video_info.cache_info()
        self.assertEqual(cache_info2.hits, 1)
        self.assertEqual(cache_info2.misses, 1)
        self.assertEqual(info1, info2)

    def test_ffmpeg_has_encoder_cache(self):
        res1 = convert._ffmpeg_has_encoder('libx264')
        res2 = convert._ffmpeg_has_encoder('libx264')
        self.assertEqual(res1, res2)
        cache_info = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(cache_info.hits, 1)

    def test_find_video_files(self):
        scan_dir = os.path.join(self.temp_dir, "scan_test")
        os.makedirs(scan_dir, exist_ok=True)
        f1 = os.path.join(scan_dir, "vid1.mp4")
        f2 = os.path.join(scan_dir, "vid2_mask.mkv")
        f3 = os.path.join(scan_dir, "doc.txt")
        open(f1, "w").close()
        open(f2, "w").close()
        open(f3, "w").close()

        all_videos = convert.find_video_files(scan_dir)
        self.assertEqual(all_videos, [f1, f2])

        filtered = convert.find_video_files(scan_dir, exclude_substrings=["_mask"])
        self.assertEqual(filtered, [f1])

    def test_metadata_performance_speedup(self):
        # Measure first call latency (uncached) vs second call latency (cached)
        convert.get_video_info.cache_clear()
        t0 = time.perf_counter()
        _ = convert.get_video_info(self.test_video)
        t1 = time.perf_counter()
        uncached_time = t1 - t0

        t2 = time.perf_counter()
        _ = convert.get_video_info(self.test_video)
        t3 = time.perf_counter()
        cached_time = t3 - t2

        self.assertLess(cached_time, uncached_time)
        print(f"\nMetadata retrieval: uncached = {uncached_time*1000:.2f}ms, cached = {cached_time*1000:.4f}ms")

if __name__ == '__main__':
    unittest.main()
