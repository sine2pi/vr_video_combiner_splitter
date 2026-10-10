import unittest
import os
import tempfile
import shutil
import convert

class TestFindVideoFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create dummy video files and non-video files
        self.files = [
            "video1.mp4",
            "video2.MKV",
            "video3.mov",
            "video4_mask.mp4",
            "ignore.txt",
            "image.png"
        ]
        for f in self.files:
            open(os.path.join(self.test_dir, f), "w").close()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_video_files_filtering(self):
        found = convert.find_video_files(self.test_dir, exclude_substrings=["_mask"])
        filenames = [os.path.basename(f) for f in found]
        self.assertIn("video1.mp4", filenames)
        self.assertIn("video2.MKV", filenames)
        self.assertIn("video3.mov", filenames)
        self.assertNotIn("video4_mask.mp4", filenames)
        self.assertNotIn("ignore.txt", filenames)
        self.assertNotIn("image.png", filenames)

if __name__ == "__main__":
    unittest.main()
