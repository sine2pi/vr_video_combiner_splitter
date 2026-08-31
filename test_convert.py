import unittest
import os
import subprocess
import convert

class TestConvertVideoInfo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = "test_sample.mp4"
        # Generate a lightweight 1-second synthetic dummy MP4 video using ffmpeg
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=1:size=640x480:rate=30",
            "-c:v", "libx264",
            cls.test_video
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def setUp(self):
        convert._get_video_info_cached.cache_clear()

    def test_get_video_info_correctness(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 480)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0, places=1)

    def test_path_normalization_cache_hit(self):
        p1 = self.test_video
        p2 = os.path.abspath(self.test_video)
        p3 = f"./{self.test_video}"

        info1 = convert.get_video_info(p1)
        info2 = convert.get_video_info(p2)
        info3 = convert.get_video_info(p3)

        self.assertEqual(info1, info2)
        self.assertEqual(info2, info3)

        cache_info = convert._get_video_info_cached.cache_info()
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(cache_info.hits, 2)

if __name__ == '__main__':
    unittest.main()
