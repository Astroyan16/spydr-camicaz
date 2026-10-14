"""Test observation filenames with real Yorick and no camera access."""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from check_freerun import extract

repo = Path(__file__).resolve().parents[2]
roots = [repo / "PC TP IR/TP_Master_version"] + [
    repo / "dist" / name for name in
    ("spydr_camicaz_test_existing_yorick", "spydr_camicaz_portable_test")
]
functions = []
for root in roots:
    folder = root / "yCamicaz/yorick/spydr"
    tree = ET.parse(folder / "spydr.glade")
    items = tree.find(".//widget[@id='combotype']/property[@name='items']")
    assert items.text.splitlines() == ["Calibration", "Science", "Test"]
    functions.append(extract((folder / "spydr_widgetcam.i").read_text(),
                             "func", "create_cam_filename"))
assert functions[0] == functions[1] == functions[2]
code = functions[0] + '''
func check(ok) { if (!ok) error,"camera filename regression"; }
func timestamp(void) { return "Wed Oct 14 12:34:56 2026"; }
prefixes=["Cal","Sci","Test"];
filters=["dark","J","H","K"];
exposures=["75ms","90ms","110ms","173ms","277ms","485ms","1110ms"];
for (kind=0;kind<3;kind++) {
  for (filt=0;filt<4;filt++) {
    for (exposure=0;exposure<7;exposure++) {
      create_cam_filename,name,kind,"aucun",10,filt,exposure,0;
      expected=prefixes(kind+1)+"-aucun-Oct14-2026-1234-"+
               filters(filt+1)+"-"+exposures(exposure+1);
      check,name==expected;
    }
  }
}
create_cam_filename,name,2,"",1,0,0,0;
check,name=="Test-unknown-Oct14-2026-1234-dark-75ms";
write,"PASS camera filenames: 84 combinations, empty object, bundle parity";
quit;
'''
with tempfile.TemporaryDirectory(prefix="spydr-filename-") as directory:
    script = Path(directory) / "check.i"
    script.write_text(code)
    result = subprocess.run(["yorick", "-batch", str(script)],
                            capture_output=True, text=True, timeout=20)
    print(result.stdout + result.stderr)
    assert result.returncode == 0 and "PASS camera filenames" in result.stdout
