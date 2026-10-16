"""Run production recording functions in Yorick with simulated camera and FITS IO."""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from check_freerun import extract


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"
text = (SOURCE / "spydr_widgetcam.i").read_text()
names = ["cam_chop_pattern", "cam_record_controls", "cam_unique_filename",
         "cam_finish_record", "apply_param", "record_image", "add_image",
         "camdata_save", "abort_record"]
code = "\n".join(extract(text, "func", name) for name in names)
tree = ET.parse(SOURCE / "spydr.glade")
labels = tree.find(".//widget[@id='comboseq']/property[@name='items']").text.splitlines()
assert labels == ["ABAB", "ABBA", "2A2B", "5A5B", "10A10B", "ABBABAABBAABABBA"]

code += '''
func check(ok,message) { if (!ok) error,message; }
func cam_stop_freerun(void) { extern cam_freerun,pending; cam_freerun=0; pending=0; }
func create_cam_filename(&name,kind,obj,count,filt,exp,lat) { name="sequence"; }
func cam_get_image(handle) {
  if (fail_prime) error,"injected primer failure";
  return -array(999,2,2,2);
}
func cam_is_open(handle) { return camera_open; }
func cam_set_param(handle,exp,lat,filt) { if (fail_apply) error,"injected Apply failure"; }
func cam_get_next_image(handle) {
  extern observed,reads,camera_open;
  if (fail_read) error,"injected camera read failure";
  grow,observed,test_dtr_state;
  reads++;
  if (fail_after_read) camera_open=0;
  return -array(reads,2,2,2);
}
func cam_chopping(handle,state) {
  extern test_dtr_state,commands;
  if (fail_chop) error,"injected chopping failure";
  check,state==0 || state==1,"invalid DTR state";
  test_dtr_state=state;
  grow,commands,state;
}
func pause(delay) {
  extern pauses;
  check,delay==500,"settling delay changed";
  pauses++;
}
func after(delay,callback) {
  extern pending,max_pending;
  if (structof(delay)==[]) { pending=0; return; }
  pending++;
  max_pending=max(max_pending,pending);
}
func spydr_pyk(message) {
  if (strmatch(message,"glade.get_widget('record').set_sensitive(1)"))
    check,!cam_recording,"Record unlocked before save completed";
}
func spydr_pyk_status_push(message) { extern last_status; last_status=message; }
func cam_load(void) { extern loads; loads++; }
func fits_write(filename,data,overwrite=) {
  extern saves,saved_count;
  if (fail_save) error,"injected disk failure";
  check,cam_recording,"save ran without acquisition lock";
  saves++;
  check,filename=="/chosen/night/sequence.fits" || filename=="/chosen/night/sequence-partial.fits","wrong save path";
  check,overwrite==0,"save would overwrite an existing file";
  check,dimsof(data)(1)==3 || dimsof(data)(1)==4,"wrong saved cube rank";
  if (dimsof(data)(1)==3) saved_count=1;
  else saved_count=dimsof(data)(5);
  check,saved_count==cam_seqind,"saved cube lost or added exposures";
  if (saved_count==1) check,allof(data==1),"single exposure is not the acquired frame";
  else for (i=1;i<=saved_count;i++)
    check,allof(data(,,,i)==i),"saved frames reordered or primer retained";
}
func run_case(mode,repeats,initial,expected) {
  extern test_dtr_state,observed,commands,reads,pauses,saves,loads,pending,max_pending;
  extern cam_freerun;
  test_dtr_state=initial; observed=commands=[];
  reads=pauses=saves=loads=pending=max_pending=0;
  cam_freerun=1;
  record_image,0,"target",repeats,"/chosen/night",mode,0,0,0;
  while (pending) {
    pending--;
    check,reads<=numberof(expected),"sequence did not terminate";
    add_image;
  }
  check,!cam_freerun,"record did not stop freerun";
  check,reads==numberof(expected),"wrong exposure count";
  if (!allof(observed==expected)) {
    write,"mode, repeats, initial:",mode,repeats,initial;
    write,"observed:",observed;
    write,"expected:",expected;
    error,"wrong chopping pattern or initial position";
  }
  check,saves==1 && loads==1,"sequence not saved exactly once";
  check,!cam_recording,"finished sequence still locked";
  check,cam_seqind==cam_nimseq && cam_nimseq==reads,"wrong progress total";
  check,max_pending<=1,"duplicate acquisition callbacks";
  if (mode<0) check,numberof(commands)==0 && pauses==0,"unchopped run moved hardware";
  else {
    transitions=1+sum(expected(2:)!=expected(:-1));
    check,numberof(commands)==transitions,"redundant or missing DTR commands";
    check,pauses==reads,"settling delay not preserved";
  }
}
cam_handle=0; cmd_cam="";
cam_recording=0; cam_applied_params=[0,0,0];
camera_open=1; fail_read=fail_after_read=fail_save=fail_chop=fail_apply=fail_prime=0;
func check_abort(void) {
  extern test_dtr_state,observed,commands,reads,pauses,saves,loads,pending,max_pending;
  test_dtr_state=1; observed=commands=[];
  reads=pauses=saves=loads=pending=max_pending=0;
  record_image,0,"target",3,"/chosen/night",4,0,0,0;
  check,reads==1 && pending==1,"missing first exposure before abort";
  abort_record;
  check,!cam_recording && pending==0,"Stop did not finish and cancel callback";
  add_image;
  check,reads==1 && saves==1 && saved_count==1 && pending==0,
    "abort did not save exactly the acquired exposure";
}
func check_invalid(mode,count) {
  extern cam_freerun;
  cam_freerun=1;
  record_image,0,"target",count,"/chosen/night",mode,0,0,0;
  return cam_freerun && !cam_recording && cam_seqind==0;
}
check_abort;
check,check_invalid(6,1),"unknown mode accepted";
check,check_invalid(-2,1),"unknown negative mode accepted";
check,check_invalid(0,0),"zero count accepted";
check,check_invalid(0,-1),"negative count accepted";
check,check_invalid(0,1.5),"fractional count accepted";

// Apply must succeed and match all three selections before Record starts.
cam_applied_params=[];
record_image,0,"target",1,"/chosen/night",0,0,0,0;
check,!cam_recording && cam_seqind==0 && strmatch(last_status,"Apply"),"missing Apply accepted";
fail_apply=1;
apply_param,0,0,0;
check,numberof(cam_applied_params)==0,"failed Apply confirmed parameters";
fail_apply=0;
apply_param,0,0,0;
record_image,0,"target",1,"/chosen/night",0,1,0,0;
check,!cam_recording && cam_seqind==0,"unapplied exposure accepted";
record_image,0,"target",1,"/chosen/night",0,0,1,0;
check,!cam_recording && cam_seqind==0,"unapplied latency accepted";
record_image,0,"target",1,"/chosen/night",0,0,0,1;
check,!cam_recording && cam_seqind==0,"unapplied filter accepted";

// A disk failure keeps valid data and the lock; Stop retries without trimming twice.
reads=0;
record_image,0,"target",3,"/chosen/night",4,0,0,0;
fail_save=1;
abort_record;
check,cam_recording && pending==0 && dimsof(cam_buffer)(5)==2,"disk failure lost cube or lock";
before=cam_seqind;
record_image,0,"target",1,"/chosen/night",0,0,0,0;
check,cam_recording && cam_seqind==before,"new Record overwrote unsaved data";
fail_save=0;
abort_record;
check,!cam_recording && saved_count==1,"Stop retry failed";

// Read and chopping failures save only previously validated frames.
for (failure=0;failure<3;failure++) {
  reads=0;
  record_image,0,"target",3,"/chosen/night",0,0,0,0;
  if (failure==0) fail_read=1;
  if (failure==1) fail_after_read=1;
  if (failure==2) fail_chop=1;
  pending--;
  add_image;
  check,!cam_recording && pending==0 && saved_count==1,
    "failure appended invalid frame or left acquisition pending";
  check,strmatch(last_status,"Record stopped:"),"failure was not reported";
  fail_read=fail_after_read=fail_chop=0; camera_open=1;
}
camera_open=0;
before=saves;
record_image,0,"target",1,"/chosen/night",0,0,0,0;
check,!cam_recording && saves==before && cam_seqind==0,"closed camera saved primer";
camera_open=1;
before=saves;
fail_prime=1;
record_image,0,"target",1,"/chosen/night",0,0,0,0;
check,!cam_recording && saves==before && pending==0,"primer failure was not cleaned up";
fail_prime=0;
fail_read=1;
record_image,0,"target",1,"/chosen/night",0,0,0,0;
check,!cam_recording && saves==before && pending==0,"first read failure saved invalid data";
fail_read=0;

// Complete cubes also remain retryable after a disk error.
reads=0;
record_image,0,"target",1,"/chosen/night",0,0,0,0;
fail_save=1;
pending--;
add_image;
check,cam_recording && pending==0 && cam_seqind==2,"completed cube was not retained";
fail_save=0;
abort_record;
check,!cam_recording && saved_count==2,"complete cube retry failed";
'''
patterns = [[0, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0] * 5 + [1] * 5,
            [0] * 10 + [1] * 10,
            [int(letter == "B") for letter in "ABBABAABBAABABBA"]]
assert len(patterns[5]) == 16 and sum(patterns[5]) == 8
cases = 0
for mode, pattern in enumerate(patterns):
    for repeats in (1, 3):
        for initial in (0, 1):
            values = ",".join(map(str, pattern * repeats))
            code += f"run_case,{mode},{repeats},{initial},[{values}];\n"
            cases += 1
for repeats in (1, 3):
    for initial in (0, 1):
        values = ",".join(map(str, [initial] * repeats))
        code += f"run_case,-1,{repeats},{initial},[{values}];\n"
        cases += 1
for mode in (1, 5):
    values = ",".join(map(str, patterns[mode] * 200))
    code += f"run_case,{mode},200,1,[{values}];\n"
    cases += 1
code += f'write,"PASS chopping sequences: {cases} recordings, all modes and 200-cycle ABBA/custom runs";\nquit;\n'

with tempfile.TemporaryDirectory(prefix="spydr-chopping-") as folder:
    script = Path(folder) / "check.i"
    script.write_text(code)
    result = subprocess.run(["yorick", "-batch", str(script)],
                            capture_output=True, text=True, timeout=30)
    print(result.stdout + result.stderr)
    assert result.returncode == 0 and "PASS chopping sequences" in result.stdout
