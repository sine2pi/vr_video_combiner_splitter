import unittest
import tempfile
import os
import shutil
from convert import find_video_files, VIDEO_EXTENSIONS

class TestFindVideoFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_finds_all_supported_extensions(self):
        created = []
        for ext in VIDEO_EXTENSIONS:
            path = os.path.join(self.test_dir, f"sample{ext}")
            with open(path, "w") as f:
                f.write("")
            created.append(path)
        # Also create a non-video file
        with open(os.path.join(self.test_dir, "sample.txt"), "w") as f:
            f.write("")

        results = find_video_files(self.test_dir)
        self.assertEqual(results, sorted(created))

    def test_excludes_specified_substrings(self):
        v1 = os.path.join(self.test_dir, "clip1.mp4")
        v2 = os.path.join(self.test_dir, "clip1_mask.mp4")
        v3 = os.path.join(self.test_dir, "clip2.mkv")
        for p in (v1, v2, v3):
            with open(p, "w") as f:
                f.write("")

        results = find_video_files(self.test_dir, exclude_substrings=["_mask"])
        self.assertEqual(results, sorted([v1, v3]))

    def test_empty_directory(self):
        results = find_video_files(self.test_dir)
        self.assertEqual(results, [])

    def test_nonexistent_directory(self):
        results = find_video_files(os.path.join(self.test_dir, "nonexistent"))
        self.assertEqual(results, [])

    def test_subdirectories_ignored(self):
        sub_dir = os.path.join(self.test_dir, "subfolder.mp4")
        os.makedirs(sub_dir)
        v1 = os.path.join(self.test_dir, "real_video.mp4")
        with open(v1, "w") as f:
            f.write("")

        results = find_video_files(self.test_dir)
        self.assertEqual(results, [v1])

if __name__ == '__main__':
    unittest.main()
