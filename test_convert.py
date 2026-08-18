import unittest
import os
import time
import subprocess
import convert

class TestConvert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_sample.mp4"
        if not os.path.exists(cls.test_video):
            cmd = [
                'ffmpeg', '-hide_banner', '-y',
                '-f', 'lavfi', '-i', 'testsrc=duration=1:size=1280x720:rate=30',
                '-c:v', 'libx264',
                cls.test_video
            ]
            subprocess.run(cmd, check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['codec'], 'h264')

    def test_path_normalization_cache_hit(self):
        # Clear cache before testing
        convert._get_video_info_cached.cache_clear()

        path_rel = self.test_video
        path_dot_rel = os.path.join(".", self.test_video)
        path_abs = os.path.abspath(self.test_video)

        # Call with relative path
        info1 = convert.get_video_info(path_rel)
        cache_info_1 = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache_info_1.hits, 0)
        self.assertEqual(cache_info_1.misses, 1)

        # Call with ./ relative path - should hit LRU cache
        info2 = convert.get_video_info(path_dot_rel)
        cache_info_2 = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache_info_2.hits, 1)
        self.assertEqual(cache_info_2.misses, 1)

        # Call with absolute path - should hit LRU cache
        info3 = convert.get_video_info(path_abs)
        cache_info_3 = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache_info_3.hits, 2)
        self.assertEqual(cache_info_3.misses, 1)

        self.assertEqual(info1, info2)
        self.assertEqual(info2, info3)

if __name__ == '__main__':
    unittest.main()
