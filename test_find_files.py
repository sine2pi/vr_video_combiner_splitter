import os
import shutil
import tempfile
import unittest
from convert import find_video_files, VIDEO_EXTENSIONS

class TestFindVideoFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_find_all_video_extensions(self):
        created_files = []
        for ext in VIDEO_EXTENSIONS:
            filename = f"test_video{ext}"
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, "w") as f:
                f.write("dummy")
            created_files.append(filepath)

        # Create non-video files
        with open(os.path.join(self.test_dir, "doc.txt"), "w") as f:
            f.write("text")

        found = find_video_files(self.test_dir)
        self.assertEqual(found, sorted(created_files))

    def test_exclude_substrings(self):
        v1 = os.path.join(self.test_dir, "video1.mp4")
        v2 = os.path.join(self.test_dir, "video2_mask.mp4")
        v3 = os.path.join(self.test_dir, "video3.mkv")
        for path in (v1, v2, v3):
            with open(path, "w") as f:
                f.write("dummy")

        found = find_video_files(self.test_dir, exclude_substrings=["_mask"])
        self.assertEqual(found, sorted([v1, v3]))

    def test_empty_and_nonexistent_directory(self):
        self.assertEqual(find_video_files(self.test_dir), [])
        non_existent = os.path.join(self.test_dir, "non_existent_folder")
        self.assertEqual(find_video_files(non_existent), [])

if __name__ == "__main__":
    unittest.main()
