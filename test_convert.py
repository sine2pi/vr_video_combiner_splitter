import unittest
import os
import subprocess
import convert

class TestConvertPathNormalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_file = os.path.abspath("test_dummy.mp4")
        # Generate a dummy test mp4 video for probe tests
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', 'testsrc=duration=1:size=1280x720:rate=30',
            '-c:v', 'libx264',
            cls.test_file
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)

    def test_path_normalization_lru_cache(self):
        convert._get_video_info_cached.cache_clear()

        rel_path = "test_dummy.mp4"
        rel_path_with_dot = os.path.join(".", "test_dummy.mp4")
        abs_path = self.test_file

        # Call with relative path
        info1 = convert.get_video_info(rel_path)
        cache1 = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache1.hits, 0)
        self.assertEqual(cache1.misses, 1)

        # Call with relative path containing ./
        info2 = convert.get_video_info(rel_path_with_dot)
        cache2 = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache2.hits, 1)
        self.assertEqual(cache2.misses, 1)

        # Call with absolute path
        info3 = convert.get_video_info(abs_path)
        cache3 = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache3.hits, 2)
        self.assertEqual(cache3.misses, 1)

        # Verify returned metadata is consistent
        self.assertEqual(info1, info2)
        self.assertEqual(info2, info3)
        self.assertEqual(info1['width'], 1280)
        self.assertEqual(info1['height'], 720)
        self.assertEqual(info1['fps'], 30.0)

if __name__ == '__main__':
    unittest.main()
