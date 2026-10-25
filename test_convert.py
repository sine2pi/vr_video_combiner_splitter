import unittest
import os
import tempfile
import shutil
import subprocess
import convert

class TestConvertOptimizations(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ffmpeg_has_encoder_and_filter_caching(self):
        # Reset cache stats before test
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

        # First call should execute and populate cache (miss)
        res1 = convert._ffmpeg_has_encoder('libx264')
        info1 = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(info1.misses, 1)
        self.assertEqual(info1.hits, 0)

        # Second call with same argument should hit cache
        res2 = convert._ffmpeg_has_encoder('libx264')
        info2 = convert._ffmpeg_has_encoder.cache_info()
        self.assertEqual(res1, res2)
        self.assertEqual(info2.hits, 1)

        # Filter check caching test
        f_res1 = convert._ffmpeg_has_filter('v360')
        f_info1 = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(f_info1.misses, 1)

        f_res2 = convert._ffmpeg_has_filter('v360')
        f_info2 = convert._ffmpeg_has_filter.cache_info()
        self.assertEqual(f_res1, f_res2)
        self.assertEqual(f_info2.hits, 1)

    def test_find_video_files(self):
        # Create dummy test files
        files_to_create = [
            'vid1.mp4',
            'vid2.mkv',
            'vid3.mov',
            'vid_mask.mp4',
            'not_a_video.txt',
            'sub/nested.mp4'
        ]
        for rel_path in files_to_create:
            full_path = os.path.join(self.temp_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write('dummy')

        found_all = convert.find_video_files(self.temp_dir)
        expected_names = ['vid1.mp4', 'vid2.mkv', 'vid3.mov', 'vid_mask.mp4']
        self.assertEqual([os.path.basename(p) for p in found_all], expected_names)

        # Test exclude substrings
        found_excluded = convert.find_video_files(self.temp_dir, exclude_substrings=['_mask'])
        expected_excluded = ['vid1.mp4', 'vid2.mkv', 'vid3.mov']
        self.assertEqual([os.path.basename(p) for p in found_excluded], expected_excluded)

    def test_get_video_info_and_duration_with_real_media(self):
        # Create a tiny 1-second sample video using ffmpeg
        video_path = os.path.join(self.temp_dir, 'sample.mp4')
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'testsrc=duration=1:size=640x360:rate=30',
            '-c:v', 'libx264', video_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        convert.get_video_info.cache_clear()

        info = convert.get_video_info(video_path)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 360)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['duration'], 1.0, delta=0.2)

        # Test wrappers
        self.assertEqual(convert.frame_rate(video_path), 30.0)
        self.assertEqual(convert.vcodec(video_path), 'h264')
        self.assertEqual(convert.vresolution(video_path), (640, 360))

        # Test video_duration uses cached info
        dur = convert.video_duration(video_path)
        self.assertAlmostEqual(dur, 1.0, delta=0.2)

        # Ensure cache hit was registered
        cache_info = convert.get_video_info.cache_info()
        self.assertGreater(cache_info.hits, 0)

if __name__ == '__main__':
    unittest.main()
