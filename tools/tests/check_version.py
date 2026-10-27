"""Check release metadata and the Python 2 GUI initialization with GTK doubles."""
from pathlib import Path
from types import SimpleNamespace
import os
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"


class Widget:
    def set_title(self, value):
        self.title = value

    def set_name(self, value):
        self.name = value

    def set_version(self, value):
        self.version = value

    def set_logo(self, value):
        self.logo = value

    def set_comments(self, value):
        self.comments = value


class VersionTests(unittest.TestCase):
    def test_metadata(self):
        version = (SOURCE / "VERSION").read_text().strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+[a-z]?$")
        info = (SOURCE / "spydr.info").read_text()
        spec = (SOURCE / "yorick-spydr.spec").read_text()
        self.assertEqual(re.search(r"^Version: (.+)$", info, re.M)[1], version)
        self.assertEqual(re.search(r"^%define version (.+)$", spec, re.M)[1], version)
        self.assertIn("**" + version + "**", (ROOT / "README.md").read_text())

    def test_gui_uses_copied_version_and_preserves_title(self):
        source = (SOURCE / "spydr.py").read_text()
        start = source.index("      self.spydrtop = spydrtop")
        end = source.index("      # handle destroy event", start)
        import textwrap
        initialization = textwrap.dedent(source[start:end])
        with tempfile.TemporaryDirectory() as folder:
            # A different version proves the GUI does not hardcode the release.
            (Path(folder) / "VERSION").write_text("9.8.7\n")
            window, about = Widget(), Widget()
            widgets = {"window1": window, "aboutdialog": about}
            glade = SimpleNamespace(get_widget=widgets.__getitem__)
            gtk = SimpleNamespace(
                glade=SimpleNamespace(XML=lambda path: glade),
                gdk=SimpleNamespace(pixbuf_new_from_file=lambda path: path),
                window_set_default_icon_list=lambda *icons: None)
            gui = SimpleNamespace()
            exec(initialization, dict(self=gui, spydrtop=folder, os=os, gtk=gtk,
                                     gobject=SimpleNamespace(GError=RuntimeError),
                                     spydr_showlower=1, spydr_dpi=100,
                                     spydr_showplugins=1))
            self.assertEqual(window.title, "Spydr / Camicaz v9.8.7")
            self.assertEqual(about.version, "9.8.7")
            yorick = (SOURCE / "spydr.i").read_text()
            for command in re.findall(r'format="(window\.set_title\([^\n]+?)"', yorick):
                command = command.replace("%s", "image.fits")
                exec("self." + command, {"self": gui})
                self.assertEqual(window.title, gui.app_title + " - image.fits")


if __name__ == "__main__":
    unittest.main()
