import unittest
import convert

class TestFFmpegCache(unittest.TestCase):
    def test_ffmpeg_has_encoder_caching(self):
        # Clear cache before test
        convert._ffmpeg_has_encoder.cache_clear()

        # First call (populates cache)
        res1 = convert._ffmpeg_has_encoder('libx264')

        # Second call (cache hit)
        res2 = convert._ffmpeg_has_encoder('libx264')

        self.assertEqual(res1, res2)
        # Verify cache hit count is incremented
        self.assertEqual(convert._ffmpeg_has_encoder.cache_info().hits, 1)

    def test_ffmpeg_has_filter_caching(self):
        # Clear cache before test
        convert._ffmpeg_has_filter.cache_clear()

        # First call
        res1 = convert._ffmpeg_has_filter('v360')

        # Second call
        res2 = convert._ffmpeg_has_filter('v360')

        self.assertEqual(res1, res2)
        # Verify cache hit count is incremented
        self.assertEqual(convert._ffmpeg_has_filter.cache_info().hits, 1)

if __name__ == '__main__':
    unittest.main()
