"""Exercise production snapshot/freerun conversions in Yorick without a camera."""
from pathlib import Path
import subprocess
import tempfile

from check_freerun import extract

SOURCE = Path(__file__).resolve().parents[2] / "PC TP IR/TP_Master_version/yCamicaz/yorick"
setup = '''
func check(ok,message) { if (!ok) error,message; }
// Boundary codes, plus increasing and decreasing differences after conversion.
raw=array(0,2,2,2);
raw(,,1)=[[65535,40000],[0,32000]];
raw(,,2)=[[65535,39000],[0,32001]];
expected=65535-raw;
func cam_get_image(handle) { return raw; }
func cam_get_cube(handle,n) { return raw(,,,-:1:n); }
func yCamicaz_get_image(handle) { return raw; }
func yCamicaz_get_cube(handle,n) { return raw(,,,-:1:n); }
func cam_is_open(handle) { return 1; }
func after(delay,callback) {}
func cam_load(void) {}
func camicaz_load(void) {}
func cam_disp_select(a,b,live=) {}
func camicaz_disp_select(a,b) {}
func camicaz_disp_zoom(void) {}
func spydr_pyk(message) {}
func pyk(message) {}
cam_recording=0; cam_handle=camicaz_handle=0;
cmd_cam=cmd_camicaz="";
cam_freerun=camicaz_freerun=1; cam_freechop=-1;
cam_buffer_content=["Start","End","Diff"];
cam_current_ndisp=cam_current_bckg=camicaz_current_ndisp=0;
'''

with tempfile.TemporaryDirectory(prefix="spydr-adu-") as folder:
    for relative, buffer in (("spydr/spydr_widgetcam.i", "cam_buffer"),
                             ("widget_camicaz.i", "camicaz_buffer")):
        source = (SOURCE / relative).read_text()
        code = setup + "\n".join(extract(source, "func", name)
                                  for name in ("snap_image", "freerun_loop"))
        code += f'''
snap_image,1;
check,allof({buffer}==expected),"snapshot ADU conversion failed";
check,min({buffer})==0 && max({buffer})==65535,"boundary codes changed";
check,allof({buffer}(,,2)-{buffer}(,,1)==raw(,,1)-raw(,,2)),"Diff changed";
snap_image,3;
check,allof(dimsof({buffer})==[4,2,2,2,3]),"cube axes changed";
for (i=1;i<=3;i++) check,allof({buffer}(,,,i)==expected),"cube ADU conversion failed";
freerun_loop;
check,allof({buffer}==expected),"freerun ADU conversion failed";
write,"PASS ADU conversion";
quit;
'''
        script = Path(folder) / "check.i"
        script.write_text(code)
        result = subprocess.run(["yorick", "-batch", str(script)],
                                capture_output=True, text=True, timeout=20)
        assert result.returncode == 0 and "PASS ADU conversion" in result.stdout, result.stdout + result.stderr
        print(f"PASS ADU conversion: {relative}; snapshot, cube, freerun, boundaries and Diff")
