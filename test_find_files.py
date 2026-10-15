import unittest
import os
import shutil
import tempfile
import convert

class TestFindVideoFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_video_files_filtering_and_sorting(self):
        filenames = [
            "video2.mp4",
            "video1.mkv",
            "image.jpg",
            "doc.pdf",
            "video1_mask.mp4",
            "video3.mov",
            "video4.webm",
            "video5.avi"
        ]
        for name in filenames:
            with open(os.path.join(self.test_dir, name), "w") as f:
                f.write("test")

        files = convert.find_video_files(self.test_dir)
        expected_names = ["video1.mkv", "video1_mask.mp4", "video2.mp4", "video3.mov", "video4.webm", "video5.avi"]
        actual_names = [os.path.basename(f) for f in files]
        self.assertEqual(actual_names, sorted(expected_names))

    def test_find_video_files_with_exclude_substrings(self):
        filenames = [
            "clip1.mp4",
            "clip1_mask.mp4",
            "clip2.mp4",
            "clip2_mask.mkv"
        ]
        for name in filenames:
            with open(os.path.join(self.test_dir, name), "w") as f:
                f.write("test")

        files = convert.find_video_files(self.test_dir, exclude_substrings=["_mask"])
        actual_names = [os.path.basename(f) for f in files]
        self.assertEqual(actual_names, ["clip1.mp4", "clip2.mp4"])

    def test_find_video_files_empty_dir(self):
        files = convert.find_video_files(self.test_dir)
        self.assertEqual(files, [])

if __name__ == "__main__":
    unittest.main()
