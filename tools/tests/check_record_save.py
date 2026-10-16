"""Exercise recording saves with real Yorick FITS files in a temporary folder."""
from pathlib import Path
import json
import subprocess
import tempfile

from check_freerun import extract


SOURCE = Path(__file__).resolve().parents[2] / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"
source = (SOURCE / "spydr_widgetcam.i").read_text()
code = 'require,"fits.i";\n'
for name in ("cam_unique_filename", "camdata_save"):
    code += extract(source, "func", name)
code += '''
func check(ok,message) { if (!ok) error,message; }
func seed_cube(void) {
  extern cam_buffer,cam_seqind;
  cam_seqind=2;
  cam_buffer=array(999,2,2,2,3);
  cam_buffer(,,,2)=1; cam_buffer(,,,3)=2;
}
func rejected_overwrite(name) {
  if (catch(-1)) return 1;
  fits_write,name,array(0,2,2),overwrite=0;
  return 0;
}
'''
with tempfile.TemporaryDirectory(prefix="spydr-save-") as folder:
    code += "base=" + json.dumps(str(Path(folder) / "same-second")) + ";\n"
    code += '''
cam_filename=base;
seed_cube;
camdata_save,0;
first=cam_filename;
check,first==base+".fits","first save name wrong";
data=fits_read(first);
check,allof(dimsof(data)==[4,2,2,2,2]),"saved FITS shape wrong";
check,allof(data(,,,1)==1) && allof(data(,,,2)==2),"saved FITS contains primer or wrong data";
cam_filename=base;
seed_cube;
camdata_save,0;
check,cam_filename==base+"-001.fits","same-second collision not numbered";
check,allof(fits_read(first)==data),"previous acquisition overwritten";
check,rejected_overwrite(first),"FITS overwrite protection failed";
check,allof(fits_read(first)==data),"refused overwrite changed data";
// A failed write must not strip the primer from the in-memory cube.
seed_cube;
cam_filename=base+"/missing/sequence";
func failed_save(void) {
  if (catch(-1)) return 1;
  camdata_save,0;
  return 0;
}
check,failed_save(),"invalid directory did not fail";
check,dimsof(cam_buffer)(5)==3 && allof(cam_buffer(,,,1)==999),"failed save damaged retry cube";
cam_filename=base;
camdata_save,0;
check,cam_filename==base+"-002.fits","retry did not preserve existing files";
check,allof(fits_read(cam_filename)==data),"retry saved wrong data";
write,"PASS real FITS: collisions, no overwrite, cube integrity and save retry";
quit;
'''
    script = Path(folder) / "check.i"
    script.write_text(code)
    result = subprocess.run(["yorick", "-batch", str(script)],
                            capture_output=True, text=True, timeout=20)
    print(result.stdout + result.stderr)
    assert result.returncode == 0 and "PASS real FITS" in result.stdout
