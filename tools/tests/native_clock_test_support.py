"""Build only the production clock bindings, without NI/camera dependencies."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def build_clock_plugin(folder):
    folder = Path(folder)
    headers = ROOT / "PC TP IR/yorick.git/relocate/include"
    if not headers.is_dir():
        raise RuntimeError("Historical Yorick headers required for native clock test")
    wrapper = folder / "clock_wrapper.c"
    wrapper.write_text('''
#include "play.h"
#include "ydata.h"
extern BuiltIn Y_yCamicaz_clock, Y_yCamicaz_clock_resolution;
static char *includes[] = {0};
static BuiltIn *routines[] = {&Y_yCamicaz_clock, &Y_yCamicaz_clock_resolution, 0};
static void *values[] = {0};
static char *names[] = {"yCamicaz_clock", "yCamicaz_clock_resolution", 0};
PLUG_EXPORT char *yk_testclock(char ***, BuiltIn ***, void ***, char ***);
char *yk_testclock(char ***inc, BuiltIn ***code, void ***data, char ***vars) {
  *inc=includes; *code=routines; *data=values; *vars=names;
  return "testclock";
}
''')
    obj = folder / "clock_wrapper.o"
    subprocess.run(["gcc", "-fPIC", "-I", str(headers), "-c", str(wrapper), "-o", str(obj)], check=True)
    library = folder / "testclock.so"
    source = ROOT / "PC TP IR/TP_Master_version/yCamicaz/yCamicaz_clock.cpp"
    subprocess.run(["g++", "-std=gnu++98", "-Wall", "-Wextra", "-fPIC", "-shared",
                    "-I", str(headers), str(source), str(obj), "-lrt", "-o", str(library)], check=True)
    return 'plug_dir,_(' + json.dumps(str(folder)) + ',plug_dir());\nplug_in,"testclock";\n'


if __name__ == "__main__":
    build_clock_plugin(sys.argv[1])
