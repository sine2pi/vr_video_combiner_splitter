import os
import subprocess
import time
import pytest
import convert

@pytest.fixture(scope="module", autouse=True)
def dummy_video():
    # Setup: Create a small dummy video for testing metadata queries
    filename = "test_temp_video.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "testsrc=duration=1:size=1280x720:rate=30",
        "-c:v", "libx264",
        filename
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    yield filename
    # Teardown: Remove the temporary video
    if os.path.exists(filename):
        os.remove(filename)

def test_metadata_correctness(dummy_video):
    # Verify we extract correct properties
    fps = convert.frame_rate(dummy_video)
    codec = convert.vcodec(dummy_video)
    width, height = convert.vresolution(dummy_video)

    assert fps == 30.0
    assert codec == "h264"
    assert width == 1280
    assert height == 720

def test_metadata_performance(dummy_video):
    # Clear the lru_cache first
    convert.get_video_info.cache_clear()

    # Time the first run (cold cache, has to run ffprobe)
    start_cold = time.perf_counter()
    fps1 = convert.frame_rate(dummy_video)
    codec1 = convert.vcodec(dummy_video)
    width1, height1 = convert.vresolution(dummy_video)
    cold_duration = time.perf_counter() - start_cold

    # Time the second run (hot cache, instantaneous lookup)
    start_hot = time.perf_counter()
    fps2 = convert.frame_rate(dummy_video)
    codec2 = convert.vcodec(dummy_video)
    width2, height2 = convert.vresolution(dummy_video)
    hot_duration = time.perf_counter() - start_hot

    print(f"\nCold Cache Duration (Combined Single Probe): {cold_duration:.6f}s")
    print(f"Hot Cache Duration (Cached): {hot_duration:.6f}s")

    # Assert values match
    assert fps1 == fps2 == 30.0
    assert codec1 == codec2 == "h264"
    assert (width1, height1) == (width2, height2) == (1280, 720)

    # Hot cache should be extremely fast (typically < 1 millisecond, whereas subprocess takes > 10ms)
    assert hot_duration < cold_duration
    # Usually hot cache is > 50x faster
    speedup = cold_duration / hot_duration if hot_duration > 0 else float('inf')
    print(f"Performance Speedup: {speedup:.2f}x")
    assert speedup > 10.0
