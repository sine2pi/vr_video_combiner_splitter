import unittest
from unittest.mock import patch, MagicMock
import convert

class TestFFmpegFeatureCache(unittest.TestCase):
    def setUp(self):
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    @patch('subprocess.run')
    def test_ffmpeg_has_encoder_caching(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=" V....D libx264              libx264 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10\n V....D hevc_nvenc          NVIDIA NVENC hevc encoder\n",
            stderr=""
        )

        res1 = convert._ffmpeg_has_encoder("hevc_nvenc")
        res2 = convert._ffmpeg_has_encoder("hevc_nvenc")

        self.assertTrue(res1)
        self.assertTrue(res2)
        # Verify subprocess.run was only called ONCE due to lru_cache
        self.assertEqual(mock_run.call_count, 1)

    @patch('subprocess.run')
    def test_ffmpeg_has_filter_caching(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=" ... v360              V->V       360 degree video conversion\n",
            stderr=""
        )

        res1 = convert._ffmpeg_has_filter("v360")
        res2 = convert._ffmpeg_has_filter("v360")

        self.assertTrue(res1)
        self.assertTrue(res2)
        # Verify subprocess.run was only called ONCE due to lru_cache
        self.assertEqual(mock_run.call_count, 1)

if __name__ == '__main__':
    unittest.main()
