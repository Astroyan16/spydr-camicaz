"""Exercise the real zoom function before any image arrives (no hardware)."""
from pathlib import Path
import subprocess
import tempfile

from check_freerun import extract

repo = Path(__file__).resolve().parents[2]
source = repo / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/spydr.i"
code = extract(source.read_text(), "func", "disp_zoom")
code += '''
func check(ok) { if (!ok) error,"zoom startup regression"; }
func after(delay,callback) { extern queued; queued++; }
func get_cursor(void) { extern cursors; cursors++; return []; }
stop_zoom=0; queued=cursors=0; from_disp=0;
spydr_im=[];
disp_zoom,once=1;
check,queued==0 && cursors==0;
disp_zoom;
check,queued==1 && cursors==0;
spydr_im=[1,2,3];
disp_zoom,once=1;
check,cursors==0;
spydr_im=array(0,16,16);
disp_zoom,once=1;
check,cursors==1 && queued==1;
write,"PASS zoom startup: empty image, vector, single-shot and retry";
quit;
'''
with tempfile.TemporaryDirectory(prefix="spydr-zoom-") as directory:
    script = Path(directory) / "check.i"
    script.write_text(code)
    result = subprocess.run(["yorick", "-batch", str(script)],
                            capture_output=True, text=True, timeout=20)
    print(result.stdout + result.stderr)
    assert result.returncode == 0 and "PASS zoom startup" in result.stdout
