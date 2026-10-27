import unittest
from convert import _ffmpeg_has_encoder, _ffmpeg_has_filter

class TestFFmpegCaching(unittest.TestCase):
    def test_ffmpeg_has_encoder_caching(self):
        _ffmpeg_has_encoder.cache_clear()
        initial_info = _ffmpeg_has_encoder.cache_info()
        self.assertEqual(initial_info.hits, 0)
        self.assertEqual(initial_info.misses, 0)

        # First call (cache miss)
        res1 = _ffmpeg_has_encoder("hevc_nvenc")
        info_after_first = _ffmpeg_has_encoder.cache_info()
        self.assertEqual(info_after_first.hits, 0)
        self.assertEqual(info_after_first.misses, 1)

        # Second call (cache hit)
        res2 = _ffmpeg_has_encoder("hevc_nvenc")
        info_after_second = _ffmpeg_has_encoder.cache_info()
        self.assertEqual(res1, res2)
        self.assertEqual(info_after_second.hits, 1)
        self.assertEqual(info_after_second.misses, 1)

        # Third call (cache hit)
        res3 = _ffmpeg_has_encoder("hevc_nvenc")
        info_after_third = _ffmpeg_has_encoder.cache_info()
        self.assertEqual(res1, res3)
        self.assertEqual(info_after_third.hits, 2)
        self.assertEqual(info_after_third.misses, 1)

    def test_ffmpeg_has_filter_caching(self):
        _ffmpeg_has_filter.cache_clear()
        initial_info = _ffmpeg_has_filter.cache_info()
        self.assertEqual(initial_info.hits, 0)
        self.assertEqual(initial_info.misses, 0)

        # First call (cache miss)
        res1 = _ffmpeg_has_filter("v360")
        info_after_first = _ffmpeg_has_filter.cache_info()
        self.assertEqual(info_after_first.hits, 0)
        self.assertEqual(info_after_first.misses, 1)

        # Second call (cache hit)
        res2 = _ffmpeg_has_filter("v360")
        info_after_second = _ffmpeg_has_filter.cache_info()
        self.assertEqual(res1, res2)
        self.assertEqual(info_after_second.hits, 1)
        self.assertEqual(info_after_second.misses, 1)

if __name__ == "__main__":
    unittest.main()
