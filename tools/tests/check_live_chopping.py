"""Exercise the production Python 2 chopping callback with GTK doubles."""
from pathlib import Path
from types import SimpleNamespace
import textwrap
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"


class Widget:
    def __init__(self, active=False):
        self.active = active
        self.sensitive = None

    def get_active(self):
        return self.active

    def set_active(self, active):
        self.active = active

    def set_sensitive(self, sensitive):
        self.sensitive = sensitive


class LiveChoppingTests(unittest.TestCase):
    def test_checkbox_updates_live_backend_only(self):
        source = (SOURCE / "spydr.py").read_text()
        start = source.index("   def on_check_chop_clicked(")
        end = source.index("\n   def ", start + 1)
        namespace = {}
        exec(textwrap.dedent(source[start:end]), namespace)
        callback = namespace["on_check_chop_clicked"]
        for running in (False, True):
            with self.subTest(running=running):
                widgets = {name: Widget() for name in ("chopbox", "comboseq", "freerun")}
                widgets["freerun"].active = running
                widgets["comboseq"].active = 5
                commands = []
                gui = SimpleNamespace(glade=SimpleNamespace(get_widget=widgets.__getitem__),
                                      py2yo=commands.append)
                for enabled in (True, False, True):
                    callback(gui, Widget(enabled))
                    self.assertEqual(widgets["chopbox"].sensitive, int(enabled))
                    self.assertEqual(widgets["freerun"].active, running)
                    if enabled:
                        self.assertEqual(widgets["comboseq"].active, 5)
                expected = ["cam_set_freerun_chopping 1", "cam_set_freerun_chopping 0",
                            "cam_set_freerun_chopping 1"] if running else []
                self.assertEqual(commands, expected)
                widgets["comboseq"].active = -1
                callback(gui, Widget(True))
                self.assertEqual(widgets["comboseq"].active, 0)


if __name__ == "__main__":
    unittest.main()
