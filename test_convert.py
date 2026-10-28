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
                convert.FFMPEG_BIN, "-y",
                "-f", "lavfi", "-i", "testsrc=duration=2:size=1280x720:rate=30",
                "-c:v", "libx264",
                cls.test_video
            ]
            subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def test_get_video_info(self):
        info = convert.get_video_info(self.test_video)
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertEqual(info['fps'], 30.0)

    def test_encoder_filter_checks(self):
        self.assertTrue(convert._ffmpeg_has_filter("v360"))

if __name__ == "__main__":
    unittest.main()
