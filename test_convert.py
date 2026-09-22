import unittest
import os
import subprocess
import shutil
import tempfile
import time
from unittest.mock import patch

import convert

class TestConvertMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.temp_dir, "test_sample.mp4")
        ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
        cmd = [
            ffmpeg_bin, "-y",
            "-f", "lavfi",
            "-i", "testsrc=duration=2:size=1280x720:rate=30",
            "-c:v", "libx264",
            cls.test_video
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    def setUp(self):
        convert._cached_get_video_info.cache_clear()

    def test_get_video_info_returns_expected_keys_and_values(self):
        info = convert.get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('duration', info)

        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertEqual(info['codec'], 'h264')
        self.assertEqual(info['width'], 1280)
        self.assertEqual(info['height'], 720)
        self.assertAlmostEqual(info['duration'], 2.0, delta=0.2)

    def test_video_duration_matches_get_video_info(self):
        info = convert.get_video_info(self.test_video)
        duration = convert.video_duration(self.test_video)
        self.assertEqual(info['duration'], duration)

    def test_lru_cache_prevents_duplicate_subprocess_calls(self):
        with patch('subprocess.run', wraps=subprocess.run) as mock_run:
            info1 = convert.get_video_info(self.test_video)
            duration1 = convert.video_duration(self.test_video)
            info2 = convert.get_video_info(self.test_video)

            # Verify subprocess.run was only called ONCE across all calls
            ffprobe_calls = [
                call for call in mock_run.call_args_list
                if convert.FFPROBE_BIN in call[0][0]
            ]
            self.assertEqual(len(ffprobe_calls), 1)

    def test_path_normalization_cache_hit(self):
        rel_path = os.path.relpath(self.test_video)
        abs_path = os.path.abspath(self.test_video)

        with patch('subprocess.run', wraps=subprocess.run) as mock_run:
            convert.get_video_info(rel_path)
            convert.get_video_info(abs_path)

            ffprobe_calls = [
                call for call in mock_run.call_args_list
                if convert.FFPROBE_BIN in call[0][0]
            ]
            self.assertEqual(len(ffprobe_calls), 1)

    def test_legacy_helper_wrappers(self):
        self.assertAlmostEqual(convert.frame_rate(self.test_video), 30.0, places=1)
        self.assertEqual(convert.vcodec(self.test_video), 'h264')
        self.assertEqual(convert.vresolution(self.test_video), (1280, 720))

if __name__ == '__main__':
    unittest.main()
