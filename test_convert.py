import unittest
import os
import tempfile
import shutil
import convert

class TestConvertOptimizations(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_video_files_filtering_and_order(self):
        filenames = [
            'video1.mp4',
            'video2.MKV',
            'video3.mov',
            'video4.avi',
            'video5.webm',
            'image.png',
            'doc.txt',
            'video_mask.mp4',
        ]
        for name in filenames:
            with open(os.path.join(self.test_dir, name), 'w') as f:
                f.write('dummy')

        found = convert.find_video_files(self.test_dir)
        basenames = [os.path.basename(p) for p in found]
        expected = sorted(['video1.mp4', 'video2.MKV', 'video3.mov', 'video4.avi', 'video5.webm', 'video_mask.mp4'])
        self.assertEqual(basenames, expected)

        found_excluded = convert.find_video_files(self.test_dir, exclude_substrings=['_mask'])
        basenames_excluded = [os.path.basename(p) for p in found_excluded]
        expected_excluded = sorted(['video1.mp4', 'video2.MKV', 'video3.mov', 'video4.avi', 'video5.webm'])
        self.assertEqual(basenames_excluded, expected_excluded)

    def test_ffmpeg_has_encoder_caching(self):
        convert._ffmpeg_has_encoder.cache_clear()
        initial_info = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(initial_info.hits, 0)
        self.assertEqual(initial_info.misses, 0)

        # First call: cache miss
        res1 = convert._ffmpeg_has_encoder('libx264')
        info1 = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(info1.misses, 1)
        self.assertEqual(info1.hits, 0)

        # Second call: cache hit
        res2 = convert._ffmpeg_has_encoder('libx264')
        info2 = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(info2.misses, 1)
        self.assertEqual(info2.hits, 1)
        self.assertEqual(res1, res2)

    def test_ffmpeg_has_filter_caching(self):
        convert._ffmpeg_has_filter.cache_clear()
        initial_info = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(initial_info.hits, 0)
        self.assertEqual(initial_info.misses, 0)

        # First call: cache miss
        res1 = convert._ffmpeg_has_filter('v360')
        info1 = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(info1.misses, 1)
        self.assertEqual(info1.hits, 0)

        # Second call: cache hit
        res2 = convert._ffmpeg_has_filter('v360')
        info2 = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(info2.misses, 1)
        self.assertEqual(info2.hits, 1)
        self.assertEqual(res1, res2)

if __name__ == '__main__':
    unittest.main()
