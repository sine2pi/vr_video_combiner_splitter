import unittest
import os
import tempfile
import shutil
from convert import find_video_files

class TestFindVideoFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.files_to_create = [
            "video1.mp4",
            "video2.mkv",
            "clip.mov",
            "movie.avi",
            "stream.webm",
            "video1_mask.mp4",
            "ignore.txt",
            "photo.jpg",
            "SUB/nested.mp4"
        ]
        os.makedirs(os.path.join(self.test_dir, "SUB"))
        for fname in self.files_to_create:
            fpath = os.path.join(self.test_dir, fname)
            with open(fpath, "w") as f:
                f.write("test")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_all_video_files(self):
        result = find_video_files(self.test_dir)
        expected = sorted([
            os.path.join(self.test_dir, "clip.mov"),
            os.path.join(self.test_dir, "movie.avi"),
            os.path.join(self.test_dir, "stream.webm"),
            os.path.join(self.test_dir, "video1.mp4"),
            os.path.join(self.test_dir, "video1_mask.mp4"),
            os.path.join(self.test_dir, "video2.mkv"),
        ])
        self.assertEqual(result, expected)

    def test_find_video_files_with_exclude(self):
        result = find_video_files(self.test_dir, exclude_substrings=["_mask"])
        expected = sorted([
            os.path.join(self.test_dir, "clip.mov"),
            os.path.join(self.test_dir, "movie.avi"),
            os.path.join(self.test_dir, "stream.webm"),
            os.path.join(self.test_dir, "video1.mp4"),
            os.path.join(self.test_dir, "video2.mkv"),
        ])
        self.assertEqual(result, expected)

    def test_nonexistent_directory(self):
        result = find_video_files(os.path.join(self.test_dir, "nonexistent"))
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
