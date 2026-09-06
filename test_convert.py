import unittest
from unittest.mock import patch, MagicMock
import convert

class TestFFmpegFeatureCaching(unittest.TestCase):
    def setUp(self):
        convert._ffmpeg_has_encoder.cache_clear()
        convert._ffmpeg_has_filter.cache_clear()

    @patch('subprocess.run')
    def test_ffmpeg_has_encoder_caching(self, mock_run):
        mock_run.return_value = MagicMock(stdout=' V..... hevc_nvenc Nvidia HEVC encoder\n', stderr='')

        # First call should invoke subprocess.run
        res1 = convert._ffmpeg_has_encoder('hevc_nvenc')
        self.assertTrue(res1)
        self.assertEqual(mock_run.call_count, 1)

        # Second call with same param should use LRU cache, not calling subprocess.run again
        res2 = convert._ffmpeg_has_encoder('hevc_nvenc')
        self.assertTrue(res2)
        self.assertEqual(mock_run.call_count, 1)

        # Call with different param should invoke subprocess.run again
        res3 = convert._ffmpeg_has_encoder('libx264')
        self.assertFalse(res3)
        self.assertEqual(mock_run.call_count, 2)

    @patch('subprocess.run')
    def test_ffmpeg_has_filter_caching(self, mock_run):
        mock_run.return_value = MagicMock(stdout=' ... v360 V->V 360 video conversion\n', stderr='')

        # First call should invoke subprocess.run
        res1 = convert._ffmpeg_has_filter('v360')
        self.assertTrue(res1)
        self.assertEqual(mock_run.call_count, 1)

        # Second call with same param should use LRU cache, not calling subprocess.run again
        res2 = convert._ffmpeg_has_filter('v360')
        self.assertTrue(res2)
        self.assertEqual(mock_run.call_count, 1)

        # Call with different param should invoke subprocess.run again
        res3 = convert._ffmpeg_has_filter('nonexistent_filter')
        self.assertFalse(res3)
        self.assertEqual(mock_run.call_count, 2)

if __name__ == '__main__':
    unittest.main()
