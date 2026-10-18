import unittest
import os
import tempfile
import shutil
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.temp_dir, 'test_sample.mp4')
        cls.masked_video = os.path.join(cls.temp_dir, 'test_sample_mask.mp4')
        cls.other_file = os.path.join(cls.temp_dir, 'notes.txt')

        ffmpeg_bin = shutil.which('ffmpeg') or 'ffmpeg'
        cmd = [
            ffmpeg_bin, '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=1:size=320x240:rate=25',
            '-c:v', 'libx264', cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        shutil.copy(cls.test_video, cls.masked_video)
        with open(cls.other_file, 'w') as f:
            f.write('hello')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        convert.get_video_info.cache_clear()
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    def test_get_video_info_and_caching(self):
        info1 = convert.get_video_info(self.test_video)
        self.assertEqual(info1['width'], 320)
        self.assertEqual(info1['height'], 240)
        self.assertEqual(info1['fps'], 25.0)
        self.assertEqual(info1['codec'], 'h264')
        self.assertGreater(info1['duration'], 0.5)

        cache_before = convert.get_video_info.cache_info()
        # Relative path or different representation should hit cache due to path normalization
        rel_path = os.path.relpath(self.test_video)
        info2 = convert.get_video_info(rel_path)
        cache_after = convert.get_video_info.cache_info()

        self.assertEqual(info1, info2)
        self.assertEqual(cache_after.hits, cache_before.hits + 1)

    def test_wrappers(self):
        self.assertEqual(convert.frame_rate(self.test_video), 25.0)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (320, 240))
        self.assertGreater(convert.video_duration(self.test_video), 0.5)

    def test_ffmpeg_cache(self):
        res1 = convert._ffmpeg_has_encoder('libx264')
        cache_before = convert._ffmpeg_has_encoder.cache_info()
        res2 = convert._ffmpeg_has_encoder('libx264')
        cache_after = convert._ffmpeg_has_encoder.cache_info()

        self.assertEqual(res1, res2)
        self.assertEqual(cache_after.hits, cache_before.hits + 1)

    def test_find_video_files(self):
        all_videos = convert.find_video_files(self.temp_dir)
        self.assertEqual(len(all_videos), 2)
        self.assertIn(self.test_video, all_videos)
        self.assertIn(self.masked_video, all_videos)

        filtered = convert.find_video_files(self.temp_dir, exclude_substrings=['_mask'])
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], self.test_video)

if __name__ == '__main__':
    unittest.main()
