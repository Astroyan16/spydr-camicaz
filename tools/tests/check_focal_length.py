"""Test the production focal conversion with real Yorick, without hardware."""
from pathlib import Path
import subprocess
import tempfile
import textwrap
import xml.etree.ElementTree as ET

from check_freerun import extract

root = Path(__file__).resolve().parents[2]
source = root / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"
tree = ET.parse(source / "spydr.glade")
assert tree.find(".//widget[@id='focal_length']") is not None
assert tree.find(".//widget[@id='pixsize']/property[@name='editable']").text == "False"
python = (source / "spydr.py").read_text()
start = python.index("   def on_focal_length_value_changed")
end = python.index("\n   def ", start + 1)
callback = textwrap.dedent(python[start:end])
namespace = {}
exec(callback, namespace)
from types import SimpleNamespace
commands = []
gui = SimpleNamespace(done_init=0, py2yo=commands.append)
widget = SimpleNamespace(get_value=lambda: 10000.)
namespace["on_focal_length_value_changed"](gui, widget)
assert commands == []
gui.done_init = 1
namespace["on_focal_length_value_changed"](gui, widget)
assert commands == ["spydr_set_focal_length 10000"]

code = extract((source / "spydr.i").read_text(), "func", "spydr_set_focal_length")
code += '''
func check(ok) { if (!ok) error,"focal conversion regression"; }
func spydr_pyk(message) { extern last_message; last_message=message; }
func spydr_disp(void) { extern displays; displays++; }
func window(n) {}
func limits(void) { extern resets; resets++; }
struct Image { double pixsize,opixsize; }
spydrs=array(Image,1);
imnum=[]; spydr_pixsize=1.; displays=resets=0;
spydr_plot_in_arcsec=0; spydr_wins=[0];
spydr_set_focal_length,10000.;
check,abs(spydr_pixsize-0.8250592249883855)<1.e-12;
check,displays==0;
imnum=1; spydrs(1).opixsize=1.; spydrs(1).pixsize=2.;
spydr_set_focal_length,10000.;
check,abs(spydrs(1).opixsize-spydr_pixsize)<1.e-12;
check,abs(spydrs(1).pixsize-2.*spydr_pixsize)<1.e-12;
check,displays==1 && resets==0;
spydr_set_focal_length,20000.;
check,abs(spydrs(1).pixsize-0.8250592249883855)<1.e-12;
spydr_plot_in_arcsec=1;
spydr_set_focal_length,5000.;
check,resets==1 && displays==3;
before=spydr_pixsize;
spydr_set_focal_length,0.;
spydr_set_focal_length,-10.;
spydr_set_focal_length,1.e8;
check,spydr_pixsize==before && displays==3;
write,"PASS focal length: conversion, empty startup, rebin, defaults, invalid values";
quit;
'''
with tempfile.TemporaryDirectory(prefix="spydr-focal-") as folder:
    script = Path(folder) / "check.i"
    script.write_text(code)
    result = subprocess.run(["yorick", "-batch", str(script)],
                            capture_output=True, text=True, timeout=20)
    print(result.stdout + result.stderr)
    assert result.returncode == 0 and "PASS focal length" in result.stdout
