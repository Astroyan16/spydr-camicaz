"""Exercise and benchmark real production C++98 clocks through Yorick."""
from pathlib import Path
import subprocess
import tempfile

from native_clock_test_support import build_clock_plugin

with tempfile.TemporaryDirectory(prefix="spydr-native-clock-") as folder:
    code = build_clock_plugin(folder) + '''
func check(ok) { if (!ok) error,"native clock regression"; }
resolution=yCamicaz_clock_resolution();
check,numberof(resolution)==2 && allof(resolution>0.);
previous=yCamicaz_clock();
for (i=1;i<=1000;i++) {
  current=yCamicaz_clock();
  check,allof(current([2,4])>=0.) && allof(current([2,4])<1.e9);
  check,current(1)==long(current(1)) && current(2)==long(current(2));
  check,(current(3)-previous(3))+(current(4)-previous(4))*1.e-9>=0.;
  previous=current;
}
func bad_arguments(void) {
  if (catch(-1)) return 1;
  yCamicaz_clock,1;
  return 0;
}
check,bad_arguments();
n=50000;
clock_before=yCamicaz_clock();
for (i=1;i<=n;i++) current=yCamicaz_clock();
clock_after=yCamicaz_clock();
elapsed=(clock_after(3)-clock_before(3))+(clock_after(4)-clock_before(4))*1.e-9;
write,format="CLOCK BENCH: %.3f us/sample (Yorick loop included)\\n",elapsed/n*1.e6;
write,format="CLOCK RESOLUTION: UTC %.9g s; monotonic %.9g s\\n",resolution(1),resolution(2);
check,elapsed>0.;
write,"PASS native clock: C++98 binding, split seconds/nanoseconds, monotonicity, resolution";
quit;
'''
    script = Path(folder) / "check.i"
    script.write_text(code)
    result = subprocess.run(["yorick", "-batch", str(script)], capture_output=True, text=True, timeout=30)
    print(result.stdout + result.stderr)
    assert result.returncode == 0 and "PASS native clock" in result.stdout
