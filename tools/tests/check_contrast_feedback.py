"""Exercise production Python callbacks with synchronous GTK signal doubles."""
from pathlib import Path
import re
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
PATHS = [ROOT / "PC TP IR/TP_Master_version"] + [
    ROOT / "dist" / name for name in
    ("spydr_camicaz_test_existing_yorick", "spydr_camicaz_portable_test")
]


def methods(path):
    source = (path / "yCamicaz/yorick/spydr/spydr.py").read_text()
    result = {}
    for name in ("y_set_cmincmax", "on_cmin_value_changed", "on_cmax_value_changed"):
        match = re.search(r"^   def " + name + r"\(.*?(?=^   def |\Z)",
                          source, re.M | re.S)
        namespace = {}
        body = "\n".join(line for line in match[0].splitlines()
                         if not line.lstrip().startswith("#"))
        exec(textwrap.dedent(body), namespace)
        result[name] = namespace[name]
    return result


class Widget:
    def __init__(self, callback):
        self.value = 0
        self.callback = callback
        self.fail = False

    def set_increments(self, *args):
        pass

    def set_value(self, value):
        self.value = value
        self.callback(self)
        if self.fail:
            raise RuntimeError("simulated widget failure")

    def get_value(self):
        return self.value


class ContrastTests(unittest.TestCase):
    def make_gui(self, path):
        gui = type("GUI", (), methods(path))()
        gui.done_init = True
        gui.messages = []
        gui.py2yo = gui.messages.append
        widgets = {name: Widget(getattr(gui, "on_" + name + "_value_changed"))
                   for name in ("cmin", "cmax")}
        gui.glade = type("Glade", (), {"get_widget": lambda self, name: widgets[name]})()
        return gui, widgets

    def test_backend_updates_do_not_echo_but_manual_edits_do(self):
        for path in PATHS:
            gui, widgets = self.make_gui(path)
            for frame in range(3000):
                # Whole-frame initialization followed by zoom-region cuts.
                gui.y_set_cmincmax(-1000, 1000, 20, 1)
                gui.y_set_cmincmax(frame, frame + 100, 1, 1)
            self.assertEqual(gui.messages, [])
            widgets["cmin"].set_value(25)
            widgets["cmax"].set_value(75)
            self.assertEqual(gui.messages, ["set_cmin 25.000000", "set_cmax 75.000000"])

    def test_failure_restores_manual_controls(self):
        gui, widgets = self.make_gui(PATHS[0])
        widgets["cmax"].fail = True
        with self.assertRaises(RuntimeError):
            gui.y_set_cmincmax(10, 20, 1, 1)
        self.assertFalse(gui._updating_cuts)
        self.assertEqual(gui.messages, [])
        widgets["cmin"].set_value(12)
        self.assertEqual(gui.messages, ["set_cmin 12.000000"])


if __name__ == "__main__":
    unittest.main()
