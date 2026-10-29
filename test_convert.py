import unittest
import os
import shutil
import tempfile
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.dummy_video = os.path.join(cls.temp_dir, "test_sample.mp4")
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=2:size=1280x720:rate=30',
            '-c:v', 'libx264',
            cls.dummy_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_get_video_info_and_duration(self):
        info = convert.get_video_info(self.dummy_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)
        self.assertAlmostEqual(info['duration'], 2.0, delta=0.5)

        # Test video_duration wrapper hits cached info
        duration = convert.video_duration(self.dummy_video)
        self.assertAlmostEqual(duration, 2.0, delta=0.5)

        # Verify LRU cache hit
        cache_info = convert.get_video_info.cache_info()
        self.assertGreater(cache_info.hits, 0)

    def test_ffmpeg_feature_caches(self):
        # First call populates cache
        res1 = convert._ffmpeg_has_encoder("libx264")
        cache_before = convert._ffmpeg_has_encoder.cache_info()
        res2 = convert._ffmpeg_has_encoder("libx264")
        cache_after = convert._ffmpeg_has_encoder.cache_info()

        self.assertEqual(res1, res2)
        self.assertEqual(cache_after.hits, cache_before.hits + 1)

    def test_find_video_files(self):
        test_dir = os.path.join(self.temp_dir, "scan_test")
        os.makedirs(test_dir, exist_ok=True)

        v1 = os.path.join(test_dir, "a.mp4")
        v2 = os.path.join(test_dir, "b.mkv")
        v3_mask = os.path.join(test_dir, "a_mask.mp4")
        txt = os.path.join(test_dir, "notes.txt")

        for p in [v1, v2, v3_mask, txt]:
            with open(p, "w") as f:
                f.write("dummy")

        all_vids = convert.find_video_files(test_dir)
        self.assertEqual(len(all_vids), 3)

        no_masks = convert.find_video_files(test_dir, exclude_substrings=["_mask"])
        self.assertEqual(len(no_masks), 2)
        self.assertNotIn(v3_mask, no_masks)

if __name__ == '__main__':
    unittest.main()
