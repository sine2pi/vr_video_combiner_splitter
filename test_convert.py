import unittest
from unittest.mock import MagicMock, patch
import queue
import sys
import convert

class MockStringVar:
    def __init__(self, value=""):
        self._val = value
    def get(self):
        return self._val
    def set(self, val):
        self._val = val

class TestConvertOptimization(unittest.TestCase):
    def test_run_process_filters_empty_lines(self):
        lines_logged = []
        def mock_callback(msg):
            lines_logged.append(msg)

        cmd = [sys.executable, "-c", "print('hello'); print('  '); print('world')"]
        convert.run_process(cmd, mock_callback)

        self.assertEqual(lines_logged, [
            f"Executing: {sys.executable} -c print('hello'); print('  '); print('world')",
            "hello",
            "world"
        ])

    @patch('tkinter.StringVar', side_effect=MockStringVar)
    def test_log_queue_thread_safe(self, mock_string_var):
        root_mock = MagicMock()
        with patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.Notebook'), \
             patch('tkinter.ttk.LabelFrame'), \
             patch('tkinter.ttk.OptionMenu'), \
             patch('tkinter.Text'), \
             patch('tkinter.Scrollbar'):
            app = convert.VRSplitCombineApp(root_mock)

            # Initially queue should be empty
            self.assertTrue(app.log_queue.empty())

            # Log message
            app.log("Test log entry")
            self.assertFalse(app.log_queue.empty())
            self.assertEqual(app.log_queue.get_nowait(), "Test log entry")

    @patch('tkinter.StringVar', side_effect=MockStringVar)
    def test_poll_log_queue_caps_lines(self, mock_string_var):
        root_mock = MagicMock()
        with patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.Notebook'), \
             patch('tkinter.ttk.LabelFrame'), \
             patch('tkinter.ttk.OptionMenu'), \
             patch('tkinter.Text') as mock_text_cls, \
             patch('tkinter.Scrollbar'):

            # Setup a mock Text widget
            mock_text_inst = MagicMock()
            mock_text_cls.return_value = mock_text_inst

            # Mock index to return a line count > 1000, say 1050
            mock_text_inst.index.return_value = "1050.0"

            app = convert.VRSplitCombineApp(root_mock)

            # Enqueue some logs
            app.log_queue.put("Message 1")
            app.log_queue.put("Message 2")

            # Call poll_log_queue manually
            app.poll_log_queue()

            # Verify batch insert was called once with "\n" joined string
            mock_text_inst.insert.assert_any_call('end', "Message 1\nMessage 2\n")

            # Verify deletion happened to cap to 1000 lines (lines - 1000 = 50)
            mock_text_inst.delete.assert_called_with('1.0', '50.0')

if __name__ == '__main__':
    unittest.main()
