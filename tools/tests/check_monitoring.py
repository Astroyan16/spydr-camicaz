"""Exercise production status polling with Yorick and a simulated serial reader."""
from pathlib import Path
import argparse
import subprocess
import tempfile

from check_freerun import extract

parser = argparse.ArgumentParser()
parser.add_argument("--bundle", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
source = args.bundle if args.bundle else root / "PC TP IR/TP_Master_version"
source = source / "yCamicaz/yorick/spydr"
widget = (source / "spydr_widgetcam.i").read_text()
main = (source / "spydr.i").read_text()
assert "cam_start_auto_monitoring;" in extract(main, "func", "spydr_win_init")
assert "start_monitoring,0;" in extract(main, "func", "spydr_quit")
code = "\n".join(extract(widget, "func", name) for name in
                 ["cam_monitor_unavailable", "get_monitoring", "start_monitoring",
                  "cam_start_auto_monitoring"])
code += '''
func check(ok) { if (!ok) error,"status polling regression"; }
func after(delay,callback) {
  extern pending,max_pending,next_delay;
  if (structof(delay)==[]) { pending=0; return; }
  pending++;
  max_pending=max(max_pending,pending);
  next_delay=delay;
}
func cam_monitoring(handle) {
  extern reads;
  reads++;
  check,!cam_recording && gui_realized;
  if (fail_read) error,"simulated serial failure";
  return sample;
}
func cam_is_open(handle) { return camera_open; }
func cam_epoch(void) { return now; }
func update_probe_values(values) { extern displayed; displayed=values; }
func spydr_pyk(message) { extern unavailable; unavailable++; }
cam_monitor=cam_recording=cam_freerun=0;
gui_realized=camera_open=1;
cam_handle=0; cmd_cam="";
cam_last_probes=cam_last_probe_time=[];
pending=max_pending=reads=unavailable=fail_read=0;
sample=[50,51,52,53]; now=100.;
cam_start_auto_monitoring;
check,pending==1 && next_delay==3 && reads==0;
get_monitoring;
check,reads==1 && pending==1 && next_delay==60;
check,allof(displayed==sample*1.5) && cam_last_probe_time==100.;
// Repeated manual clicks replace rather than accumulate timers.
for (i=1;i<=1000;i++) start_monitoring,1;
check,max_pending==1 && pending==1;
before=reads;
cam_recording=1;
for (i=1;i<=1000;i++) get_monitoring;
start_monitoring,1;
check,reads==before && pending==1 && next_delay==5;
cam_recording=0; cam_freerun=1;
get_monitoring;
check,reads==before+1 && next_delay==60 && cam_freerun==1;
start_monitoring,1;
check,reads==before+2 && pending==1 && next_delay==60 && cam_freerun==1;
for (i=1;i<=1000;i++) get_monitoring;
check,reads==before+1002 && max_pending==1 && cam_freerun==1;
// Record remains protected even if a stale freerun flag is still set.
before=reads; cam_recording=1;
get_monitoring;
start_monitoring,1;
check,reads==before && pending==1 && next_delay==5;
cam_recording=0;
cam_freerun=0; gui_realized=0;
get_monitoring;
check,reads==before;
gui_realized=1; now=200.;
get_monitoring;
check,reads==before+1 && cam_last_probe_time==200. && next_delay==60;
// Invalid/absent responses never become zero-K readings or fresh FITS samples.
sample=[0,0,0,0]; now=300.;
get_monitoring;
check,cam_last_probe_time==200. && unavailable==8 && pending==1;
sample=[1,2]; get_monitoring;
check,cam_last_probe_time==200.;
camera_open=0; before=reads; get_monitoring;
check,reads==before && pending==1;
camera_open=1; fail_read=1; get_monitoring;
check,pending==1 && next_delay==60 && cam_last_probe_time==200.;
fail_read=0; sample=[54,55,56,57]; now=400.; get_monitoring;
check,cam_last_probe_time==400. && allof(cam_last_probes==sample);
start_monitoring,0;
before=reads; get_monitoring;
check,cam_monitor==0 && pending==0 && reads==before;
write,"PASS status polling: startup, 60s, freerun reads, Record deferral, bounded timer, errors, shutdown";
quit;
'''
with tempfile.TemporaryDirectory(prefix="spydr-monitor-") as folder:
    script = Path(folder) / "check.i"
    script.write_text(code)
    result = subprocess.run(["yorick", "-batch", str(script)], capture_output=True,
                            text=True, timeout=15)
    print(result.stdout + result.stderr)
    assert result.returncode == 0 and "PASS status polling" in result.stdout
