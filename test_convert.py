import unittest
import os
import tempfile
import subprocess
import time
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = tempfile.TemporaryDirectory()
        cls.test_video = os.path.join(cls.tmp_dir.name, "sample.mp4")
        # Generate a 2-second dummy MP4 video using ffmpeg
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "testsrc=duration=2:size=640x360:rate=30",
            "-c:v", "libx264", cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_dir.cleanup()

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_and_duration(self):
        info = convert.get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)

        self.assertAlmostEqual(info['fps'], 30.0, delta=0.1)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertAlmostEqual(info['duration'], 2.0, delta=0.2)

        # Test video_duration wrapper uses cache
        dur = convert.video_duration(self.test_video)
        self.assertAlmostEqual(dur, 2.0, delta=0.2)

    def test_path_normalization_cache_hit(self):
        rel_path = os.path.relpath(self.test_video)
        abs_path = os.path.abspath(self.test_video)

        # First call populates cache
        info1 = convert.get_video_info(rel_path)

        t0 = time.perf_counter()
        info2 = convert.get_video_info(abs_path)
        t1 = time.perf_counter()

        self.assertEqual(info1, info2)
        # 2nd call should take < 1 ms (LRU hit)
        self.assertLess((t1 - t0) * 1000, 10.0)

    def test_ffmpeg_has_encoder_cache(self):
        has_libx264_1 = convert._ffmpeg_has_encoder("libx264")

        t0 = time.perf_counter()
        has_libx264_2 = convert._ffmpeg_has_encoder("libx264")
        t1 = time.perf_counter()

        self.assertEqual(has_libx264_1, has_libx264_2)
        self.assertLess((t1 - t0) * 1000, 1.0)

    def test_find_video_files(self):
        with tempfile.TemporaryDirectory() as sub_dir:
            # Create video files and non-video files
            f1 = os.path.join(sub_dir, "vid1.mp4")
            f2 = os.path.join(sub_dir, "vid2_mask.mp4")
            f3 = os.path.join(sub_dir, "vid3.mkv")
            f4 = os.path.join(sub_dir, "document.pdf")

            for f in (f1, f2, f3, f4):
                open(f, 'w').close()

            all_vids = convert.find_video_files(sub_dir)
            self.assertEqual(len(all_vids), 3)
            self.assertEqual(all_vids, sorted([f1, f2, f3]))

            # Test exclude substring
            filtered_vids = convert.find_video_files(sub_dir, exclude_substrings=["_mask"])
            self.assertEqual(len(filtered_vids), 2)
            self.assertEqual(filtered_vids, sorted([f1, f3]))

if __name__ == "__main__":
    unittest.main()
