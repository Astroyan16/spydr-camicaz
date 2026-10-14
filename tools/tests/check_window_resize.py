"""Check production resize callbacks without requiring legacy PyGTK."""
from pathlib import Path
import re
import textwrap
import unittest


class Scheduler:
    def __init__(self):
        self.pending = {}
        self.serial = 0

    def timeout_add(self, delay, callback):
        self.serial += 1
        self.pending[self.serial] = callback
        return self.serial

    def source_remove(self, ident):
        del self.pending[ident]

    def fire(self):
        callback = self.pending.pop(next(iter(self.pending)))
        callback()


class ResizeTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[2] / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/spydr.py"
        source = path.read_text()
        self.scheduler = Scheduler()
        namespace = {"gobject": self.scheduler}
        callbacks = {}
        for name in ("on_camera_size_allocate", "apply_camera_size", "camera_resize_done", "destroy"):
            match = re.search(r"^   def " + name + r"\(.*?(?=^   def |\Z)", source, re.M | re.S)
            body = "\n".join(line for line in match[0].splitlines()
                             if not line.lstrip().startswith("#"))
            exec(textwrap.dedent(body), namespace)
            callbacks[name] = namespace[name]
        self.gui = type("GUI", (), callbacks)()
        self.area = type("Area", (), {"width": 480, "height": 501})()
        widget = type("Widget", (), {"get_allocation": lambda _: self.area})()
        self.gui.glade = type("Glade", (), {"get_widget": lambda _, name: widget})()
        self.gui._resize_closed = self.gui._resize_busy = False
        self.gui._resize_timer = self.gui._resize_last = None
        self.gui._resize_min_dpi = 80
        self.gui.done_init = True
        self.messages = []
        self.gui.py2yo = self.messages.append

    def test_debounce_backpressure_and_latest_size(self):
        for _ in range(1000):
            self.gui.on_camera_size_allocate(None, None)
        self.assertEqual(len(self.scheduler.pending), 1)
        self.scheduler.fire()
        self.assertEqual(len(self.messages), 1)
        self.area.width = self.area.height = 1000
        for _ in range(1000):
            self.gui.on_camera_size_allocate(None, None)
        self.assertEqual(len(self.messages), 1)
        self.assertFalse(self.scheduler.pending)
        self.gui.camera_resize_done(1)
        self.scheduler.fire()
        self.assertEqual(len(self.messages), 2)
        self.assertGreater(self.gui._resize_last[0], 80)
        self.gui.camera_resize_done(1)
        self.scheduler.fire()
        self.assertEqual(len(self.messages), 2)

    def test_minimum_and_failure(self):
        self.area.width = self.area.height = 10
        self.gui.apply_camera_size()
        self.assertEqual(self.gui._resize_last, (80, -2, -2))
        self.gui.camera_resize_done(0)
        self.assertFalse(self.gui._resize_busy)
        self.assertIsNone(self.gui._resize_last)
        self.assertFalse(self.scheduler.pending)

    def test_startup_and_destroy(self):
        self.gui.done_init = False
        self.gui.apply_camera_size()
        self.assertEqual(len(self.scheduler.pending), 1)
        self.assertFalse(self.messages)
        with self.assertRaises(SystemExit):
            self.gui.destroy(None)
        self.assertFalse(self.scheduler.pending)
        self.gui.camera_resize_done(1)
        self.assertFalse(self.scheduler.pending)


if __name__ == "__main__":
    unittest.main()
