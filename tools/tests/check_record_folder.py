"""Test the production Record callback without Python 2, GTK or camera access."""
from pathlib import Path
from types import SimpleNamespace
import os
import tempfile
import textwrap
import unittest
import base64
import json
import re
import shlex
from types import MethodType


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
        self.idle = []
        namespace = {"os": os, "gobject": SimpleNamespace(
            idle_add=lambda callback, *args: self.idle.append((callback, args)))}
        self.namespace = namespace
        exec(textwrap.dedent(source[start:end]), namespace)
        self.callback = namespace["on_record_clicked"]
        names = ("freerun", "apply_param", "acquire", "record", "button_stop",
                 "combotype", "objname", "spin_nseq", "check_chop", "num_expo",
                 "num_latency", "num_filter", "comboseq", "obsname", "comments")
        self.widgets = {name: Widget() for name in names}
        self.widgets["focal_length"] = SimpleNamespace(get_value=lambda: 10000.)
        self.commands, self.errors = [], []
        self.gui = SimpleNamespace(glade=SimpleNamespace(get_widget=self.widgets.__getitem__),
                                   py2yo=self.commands.append, pyk_error=self.errors.append)
        for name in ("cancel_pending_record", "record_parameters_checked", "confirm_record_apply", "start_pending_record", "record_apply_failed"):
            start = source.index("   def " + name + "(")
            end = source.index("\n   def ", start + 1)
            exec(textwrap.dedent(source[start:end]), namespace)
            setattr(self.gui, name, MethodType(namespace[name], self.gui))

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
                self.assertEqual(self.commands[-1],
                                 'cam_check_record_params %d 0 0 0' % self.gui._record_request_id)
                self.gui.record_parameters_checked(self.gui._record_request_id, 0)
                escaped = str(selected).replace("\\", "\\\\").replace('"', '\\"')
                self.assertTrue(self.commands[-1].startswith(
                    'cam_record_request 0 "@target" 200 "%s" -1 0 0 0 ' % escaped))
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

    def test_unicode_comments_and_quotes_are_preserved_without_command_injection(self):
        with tempfile.TemporaryDirectory() as folder:
            self.chooser(folder, folder)
            original = 'Zo\u00e9 "test" \\ notes\n' * 50
            self.widgets["obsname"].get_text = lambda: original
            self.widgets["comments"].get_text = lambda: original.encode("utf-8")
            self.widgets["objname"].get_text = lambda: "Saturne"
            self.callback(self.gui, None)
            self.gui.record_parameters_checked(self.gui._record_request_id, 0)
            command = self.commands[-1]
            self.assertNotIn("\n", command)
            encoded = shlex.split(command)[11][1:]
            metadata = json.loads(base64.b64decode(encoded))
            self.assertEqual(metadata["observer"], original)
            self.assertEqual(metadata["comments"], original)
            self.assertEqual(metadata["object"], "Saturne")
            self.assertEqual(metadata["focal_length_mm"], 10000.)

    def test_cancel_and_duplicate_request_preserve_freerun(self):
        with tempfile.TemporaryDirectory() as folder:
            self.chooser(folder, folder)
            self.widgets["freerun"].active = True
            self.callback(self.gui, None)
            self.callback(self.gui, None)
            self.assertEqual(len(self.commands), 1)
            self.gui.cancel_pending_record()
            self.assertTrue(self.widgets["record"].sensitive)
            self.assertTrue(self.widgets["freerun"].active)
            self.assertTrue(self.widgets["apply_param"].sensitive)
            self.gui.start_pending_record(self.gui._record_request_id, True)
            self.assertEqual(len(self.commands), 1)

    def test_confirmed_apply_is_single_use_and_keeps_record_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            self.chooser(folder, folder)
            self.callback(self.gui, None)
            request = self.gui._record_request_id
            self.gui.start_pending_record(request + 1, True)
            self.assertEqual(len(self.commands), 1)
            self.gui.start_pending_record(request, True)
            self.assertTrue(self.commands[-1].endswith(' 1'))
            self.assertFalse(self.widgets["record"].sensitive)
            self.gui.start_pending_record(request, True)
            self.assertEqual(len(self.commands), 2)

    def test_changed_selection_cancels_pending_record(self):
        with tempfile.TemporaryDirectory() as folder:
            self.chooser(folder, folder)
            self.callback(self.gui, None)
            self.widgets["num_filter"].active = 1
            self.gui.start_pending_record(self.gui._record_request_id, True)
            self.assertEqual(len(self.commands), 1)
            self.assertTrue(self.widgets["record"].sensitive)
            self.assertEqual(len(self.idle), 1)

    def test_modal_confirmation_apply_and_cancel(self):
        class Dialog:
            def __init__(self, **kwargs):
                self.buttons = []
                self.destroyed = False

            def format_secondary_text(self, text): pass
            def add_button(self, label, response): self.buttons.append((label, response))
            def set_default_response(self, response): self.default = response
            def run(self): return selected_response[0]
            def destroy(self): self.destroyed = True

        dialogs, selected_response = [], [-1]
        def create_dialog(**kwargs):
            dialog = Dialog(**kwargs)
            dialogs.append(dialog)
            return dialog
        self.namespace["gtk"] = SimpleNamespace(MessageDialog=create_dialog,
            DIALOG_MODAL=1, DIALOG_DESTROY_WITH_PARENT=2, MESSAGE_QUESTION=1,
            BUTTONS_NONE=0, RESPONSE_CANCEL=-1, RESPONSE_APPLY=1)
        self.gui.window = object()
        with tempfile.TemporaryDirectory() as folder:
            self.chooser(folder, folder)
            for response in (-1, 1):
                selected_response[0] = response
                self.callback(self.gui, None)
                request = self.gui._record_request_id
                self.gui.record_parameters_checked(request, 1)
                self.gui.record_parameters_checked(request, 1)
                self.assertEqual(len(self.idle), 1)
                self.assertEqual(dialogs[-1].destroyed if dialogs else True, True)
                callback, args = self.idle.pop()
                callback(*args)
                self.assertTrue(dialogs[-1].destroyed)
                self.assertEqual(dialogs[-1].default, -1)
                self.assertEqual(dialogs[-1].buttons, [('Cancel', -1), ('Apply and Record', 1)])
                if response == -1:
                    self.assertFalse(any(command.startswith('cam_record_request') for command in self.commands))
                else:
                    self.assertTrue(self.commands[-1].endswith(' 1'))

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
