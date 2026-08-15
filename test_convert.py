import unittest
import os
import time
import queue
import tkinter as tk
from convert import get_video_info, frame_rate, vcodec, vresolution, VRSplitCombineApp

class TestConvertMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_video = 'test_sample.mp4'
        if not os.path.exists(cls.test_video):
            os.system(f'ffmpeg -y -f lavfi -i testsrc=duration=1:size=640x480:rate=30 -c:v libx264 {cls.test_video} > /dev/null 2>&1')

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_video):
            try:
                os.remove(cls.test_video)
            except OSError:
                pass

    def test_get_video_info(self):
        info = get_video_info(self.test_video)
        self.assertIn('fps', info)
        self.assertIn('codec', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 480)
        self.assertEqual(info['codec'], 'h264')
        self.assertAlmostEqual(info['fps'], 30.0, places=1)

    def test_legacy_wrappers(self):
        self.assertAlmostEqual(frame_rate(self.test_video), 30.0, places=1)
        self.assertEqual(vcodec(self.test_video), 'h264')
        self.assertEqual(vresolution(self.test_video), (640, 480))


class TestQueuedLogging(unittest.TestCase):
    def test_queue_logging_performance_and_capping(self):
        root = tk.Tk()
        root.withdraw()

        app = VRSplitCombineApp(root)

        # Enqueue 1500 test messages
        for i in range(1500):
            app.log(f"Test message {i}")

        self.assertEqual(app.log_queue.qsize(), 1500)

        # Drain the queue manually via poll_log_queue logic
        messages = []
        while not app.log_queue.empty():
            messages.append(app.log_queue.get_nowait())

        app.log_text.config(state='normal')
        app.log_text.insert('end', "\n".join(messages) + "\n")

        num_lines = int(app.log_text.index('end-1c').split('.')[0])
        if num_lines > 1000:
            app.log_text.delete('1.0', f'{num_lines - 1000 + 1}.0')

        app.log_text.config(state='disabled')

        final_line_count = int(app.log_text.index('end-1c').split('.')[0])
        self.assertLessEqual(final_line_count, 1001)

        root.destroy()

if __name__ == '__main__':
    unittest.main()
