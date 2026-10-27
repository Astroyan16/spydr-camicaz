"""Exercise real metadata startup with an on-disk camera configuration."""
from pathlib import Path
import json
import subprocess
import tempfile
import argparse

from check_freerun import extract

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"
parser = argparse.ArgumentParser()
parser.add_argument("--bundle", type=Path)
args = parser.parse_args()
if args.bundle:
    SOURCE = args.bundle / "yCamicaz/yorick/spydr"

with tempfile.TemporaryDirectory(prefix="spydr-config-") as folder:
    folder = Path(folder)
    config = folder / "camicaz.ini"
    config.write_text("[camera]\nnbDims = 3\n\n[NI]\nportList = Dev1/port2,Dev1/port3\n")
    (folder / "empty.ini").write_text("")
    (folder / "no-newline.ini").write_text("[camera]\nnbDims = 3")
    code = '''
func cam_epoch(void) { return 1700000000.; }
func yCamicaz_clock_resolution(void) { return [1.e-9,1.e-9]; }
cam_last_probes=cam_last_probe_time=[];
func check(ok) { if (!ok) error,"configuration snapshot regression"; }
'''
    code += extract((SOURCE / "spydr_metadata.i").read_text(), "func", "cam_metadata_begin")
    code += '\ncamtop=' + json.dumps(str(folder)) + '; cam_config="camicaz.ini";\n'
    call = 'cam_metadata_begin,1,"target",1,-1,0,0,0,"observer","notes","",0.,"test";\n'
    code += call
    code += '''
check,numberof(cam_meta_config)==5;
check,cam_meta_config(1)=="[camera]";
check,cam_meta_config(3)=="";
check,cam_meta_config(5)=="portList = Dev1/port2,Dev1/port3";
'''
    # Repeated Records must replace, rather than append, the snapshot.
    code += call
    code += 'check,numberof(cam_meta_config)==5;\ncam_config="empty.ini";\n' + call
    code += 'check,numberof(cam_meta_config)==0;\ncam_config="no-newline.ini";\n' + call
    code += 'check,numberof(cam_meta_config)==2;\ncam_config="missing.ini";\n' + call
    code += 'check,numberof(cam_meta_config)==0;\n'
    code += 'write,"PASS metadata startup: real config, blank lines, EOF, repeated Record, missing config";\nquit;\n'
    script = folder / "check.i"
    script.write_text(code)
    result = subprocess.run(["yorick", "-batch", str(script)],
                            capture_output=True, text=True, timeout=5)
    print(result.stdout + result.stderr)
    assert result.returncode == 0 and "PASS metadata startup" in result.stdout
