import unittest
import os
import glob
import tempfile
import shutil
import time
from convert import find_video_files, VIDEO_EXTENSIONS

class TestFindVideoFiles(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_find_video_files_basic(self):
        # Create various files
        files_to_create = [
            "a_video.mp4",
            "b_clip.mkv",
            "c_movie.mov",
            "d_film.avi",
            "e_stream.webm",
            "f_mask.mp4",
            "notes.txt",
            "image.png"
        ]
        for name in files_to_create:
            open(os.path.join(self.temp_dir, name), 'w').close()

        res = find_video_files(self.temp_dir)
        expected_names = sorted([
            "a_video.mp4", "b_clip.mkv", "c_movie.mov",
            "d_film.avi", "e_stream.webm", "f_mask.mp4"
        ])
        result_names = [os.path.basename(p) for p in res]
        self.assertEqual(result_names, expected_names)

    def test_find_video_files_exclude_substrings(self):
        files_to_create = [
            "video1.mp4",
            "video1_mask.mp4",
            "video2.mkv",
            "video2_mask.mkv",
            "test_ignore.mov"
        ]
        for name in files_to_create:
            open(os.path.join(self.temp_dir, name), 'w').close()

        res = find_video_files(self.temp_dir, exclude_substrings=["_mask", "ignore"])
        result_names = [os.path.basename(p) for p in res]
        self.assertEqual(result_names, ["video1.mp4", "video2.mkv"])

    def test_find_video_files_nonexistent_dir(self):
        res = find_video_files(os.path.join(self.temp_dir, "nonexistent_folder"))
        self.assertEqual(res, [])

    def test_find_video_files_performance_benchmark(self):
        # Create 1000 files to measure performance
        for i in range(200):
            open(os.path.join(self.temp_dir, f"vid_{i}.mp4"), 'w').close()
            open(os.path.join(self.temp_dir, f"vid_{i}_mask.mp4"), 'w').close()
            open(os.path.join(self.temp_dir, f"doc_{i}.txt"), 'w').close()

        t0 = time.perf_counter()
        for _ in range(50):
            res = find_video_files(self.temp_dir, exclude_substrings=["_mask"])
        elapsed = time.perf_counter() - t0
        self.assertEqual(len(res), 200)
        print(f"\n[Benchmark] 50 runs of find_video_files on 600 files took {elapsed*1000:.2f} ms ({elapsed*20:.2f} ms/run)")

if __name__ == "__main__":
    unittest.main()
