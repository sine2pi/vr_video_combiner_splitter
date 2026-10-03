import unittest
import os
import subprocess
import convert

class TestConvertMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_file = "test.mp4"
        if not os.path.exists(cls.test_file):
            cmd = ["ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=1:size=1280x720:rate=30", "-c:v", "libx264", cls.test_file, "-y"]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_file):
            try:
                os.remove(cls.test_file)
            except OSError:
                pass

    def setUp(self):
        convert.get_video_info.cache_clear()

    def test_get_video_info(self):
        info = convert.get_video_info(self.test_file)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertAlmostEqual(info['duration'], 1.0, places=1)

    def test_wrappers(self):
        self.assertEqual(convert.frame_rate(self.test_file), 30.0)
        self.assertEqual(convert.vcodec(self.test_file), 'h264')
        self.assertEqual(convert.vresolution(self.test_file), (1280, 720))
        self.assertAlmostEqual(convert.video_duration(self.test_file), 1.0, places=1)

    def test_path_normalization_cache(self):
        info1 = convert.get_video_info(self.test_file)
        info2 = convert.get_video_info("./" + self.test_file)
        info3 = convert.get_video_info(os.path.abspath(self.test_file))
        self.assertEqual(info1, info2)
        self.assertEqual(info2, info3)
        cache_info = convert.get_video_info.cache_info()
        self.assertEqual(cache_info.hits, 2)
        self.assertEqual(cache_info.misses, 1)

if __name__ == "__main__":
    unittest.main()
