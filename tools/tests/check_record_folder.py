"""Test the production Record callback without Python 2, GTK or camera access."""
from pathlib import Path
from types import SimpleNamespace
import os
import tempfile
import textwrap
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"


class Widget:
    def __init__(self, active=0):
        self.active = active
        self.sensitive = True

    def get_active(self):
        return self.active

    def set_active(self, value):
        self.active = value

    def set_sensitive(self, value):
        self.sensitive = value

    def get_text(self):
        return "target"

    def get_value_as_int(self):
        return 200


class RecordFolderTests(unittest.TestCase):
    def setUp(self):
        source = (SOURCE / "spydr.py").read_text()
        start = source.index("   def on_record_clicked(")
        end = source.index("\n   def ", start + 1)
        namespace = {"os": os}
        exec(textwrap.dedent(source[start:end]), namespace)
        self.callback = namespace["on_record_clicked"]
        names = ("freerun", "apply_param", "acquire", "record", "button_stop",
                 "combotype", "objname", "spin_nseq", "check_chop", "num_expo",
                 "num_latency", "num_filter", "comboseq")
        self.widgets = {name: Widget() for name in names}
        self.commands, self.errors = [], []
        self.gui = SimpleNamespace(glade=SimpleNamespace(get_widget=self.widgets.__getitem__),
                                   py2yo=self.commands.append, pyk_error=self.errors.append)

    def chooser(self, selected, displayed):
        self.widgets["data_location"] = SimpleNamespace(
            get_filename=lambda: selected, get_current_folder=lambda: displayed)

    def test_first_and_subsequent_record_use_selected_folder(self):
        with tempfile.TemporaryDirectory() as parent:
            selected = Path(parent) / "night 1" / "sequence"
            selected.mkdir(parents=True)
            # Selecting a child and browsing inside it must yield the same path.
            for displayed in (parent, str(selected.parent), str(selected)):
                self.chooser(str(selected), displayed)
                self.callback(self.gui, None)
                escaped = str(selected).replace("\\", "\\\\").replace('"', '\\"')
                self.assertEqual(self.commands[-1],
                                 'record_image 0 "target" 200 "%s" -1 0 0 0' % escaped)
            self.assertEqual(self.errors, [])

    def test_invalid_selection_does_not_stop_freerun_or_lock_controls(self):
        with tempfile.TemporaryDirectory() as parent:
            file = Path(parent) / "not-a-folder"
            file.touch()
            for selected in (None, "", str(Path(parent) / "missing"), str(file)):
                with self.subTest(selected=selected):
                    self.widgets["freerun"].active = True
                    self.chooser(selected, parent)
                    self.callback(self.gui, None)
                    self.assertTrue(self.widgets["freerun"].active)
                    self.assertTrue(self.widgets["record"].sensitive)
                    self.assertTrue(self.widgets["apply_param"].sensitive)
                    self.assertEqual(self.commands, [])
            self.assertEqual(len(self.errors), 4)

    def test_stop_does_not_unlock_record_before_backend_finishes(self):
        source = (SOURCE / "spydr.py").read_text()
        start = source.index("   def on_button_stop_clicked(")
        end = source.index("\n   def ", start + 1)
        namespace = {}
        exec(textwrap.dedent(source[start:end]), namespace)
        self.widgets["record"].sensitive = False
        namespace["on_button_stop_clicked"](self.gui, None)
        self.assertFalse(self.widgets["record"].sensitive)
        self.assertEqual(self.commands, ["abort_record"])


if __name__ == "__main__":
    unittest.main()
