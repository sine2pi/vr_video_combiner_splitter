import os
import sys
import unittest
import time
import subprocess
import tkinter as tk
import convert

class TestConvertOptimizations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = 'test_sample.mp4'
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi', '-i',
            'testsrc=duration=1:size=640x360:rate=30',
            '-c:v', 'libx264', cls.test_video
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            os.remove(cls.test_video)

    def setUp(self):
        convert.get_video_info.cache_clear()

    def test_get_video_info_normalization_and_cache(self):
        path1 = self.test_video
        path2 = os.path.join('.', self.test_video)
        path3 = os.path.abspath(self.test_video)

        info1 = convert.get_video_info(path1)
        info2 = convert.get_video_info(path2)
        info3 = convert.get_video_info(path3)

        self.assertEqual(info1['fps'], 30.0)
        self.assertEqual(info1['codec'], 'h264')
        self.assertEqual(info1['width'], 640)
        self.assertEqual(info1['height'], 360)

        self.assertEqual(info1, info2)
        self.assertEqual(info2, info3)

        cache_info = convert.get_video_info.cache_info()
        self.assertEqual(cache_info.misses, 1)
        self.assertEqual(cache_info.hits, 2)

    def test_legacy_wrappers(self):
        fps = convert.frame_rate(self.test_video)
        codec = convert.vcodec(self.test_video)
        width, height = convert.vresolution(self.test_video)

        self.assertEqual(fps, 30.0)
        self.assertEqual(codec, 'h264')
        self.assertEqual((width, height), (640, 360))

    def test_app_logging_and_capping(self):
        root = tk.Tk()
        app = convert.VRSplitCombineApp(root)

        for i in range(1200):
            app.log(f'Log line {i}')

        app.poll_log_queue()
        lines = app.log_text.get('1.0', 'end-1c').strip().split('\n')

        self.assertEqual(len(lines), 1000)
        self.assertEqual(lines[0], 'Log line 200')
        self.assertEqual(lines[-1], 'Log line 1199')

        root.destroy()

    def test_benchmark_metadata_caching(self):
        convert.get_video_info.cache_clear()

        start = time.perf_counter()
        for _ in range(20):
            convert.get_video_info(self.test_video)
            convert.get_video_info(f'./{self.test_video}')
            convert.get_video_info(os.path.abspath(self.test_video))
        elapsed = time.perf_counter() - start

        print(f'\n[BENCHMARK] 60 metadata queries executed in {elapsed*1000:.2f} ms')
        self.assertLess(elapsed, 0.5)

if __name__ == '__main__':
    unittest.main()
