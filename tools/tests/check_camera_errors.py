"""Compile real wrapper/setter functions against small C++98 hardware doubles."""
from pathlib import Path
import subprocess
import tempfile

from check_freerun import extract


ROOT = Path(__file__).resolve().parents[2] / "PC TP IR/TP_Master_version"
wrapper = (ROOT / "yCamicaz/yCamicaz.cpp").read_text()
library = (ROOT / "libcamicaz/src/camicaz.cpp").read_text()
code = r'''
#include <cassert>
#include <cstdio>
#include <iostream>
#include <stdexcept>
using namespace std;
enum { TIOCMGET=1, TIOCMSET=2, TIOCM_DTR=4 };
int fail_ioctl=0, line_status=0;
int ioctl(int, int request, int *status) {
  if (request==fail_ioctl) return -1;
  if (request==TIOCMGET) *status=line_status;
  else line_status=*status;
  return 0;
}
void usleep(int) {}
class Camicaz {
public:
  int expo,latency,filter,chopping,serialFdChopping;
  int serialCam,serial_error,serial_calls,image_error,image_calls,fail_image_at,serial_fail_at;
  bool camOpen,camAcquire;
  long dimensions[3];
  Camicaz(): expo(0),latency(0),filter(0),chopping(0),serialFdChopping(1),
    serialCam(1),serial_error(0),serial_calls(0),image_error(0),image_calls(0),
    fail_image_at(0),serial_fail_at(0),camOpen(true),camAcquire(false) {
    dimensions[0]=2; dimensions[1]=2; dimensions[2]=2;
  }
  int sendCmd(int, const char*, int, bool) {
    ++serial_calls;
    return serial_calls==serial_fail_at ? -2 : serial_error;
  }
  int setExpo(int); int setLatency(int); int setFilter(int); int setParam(int,int,int);
  int setChopping(int);
  long getNbDims() { return 3; }
  long *getDims() { return dimensions; }
  long getSize() { return 8; }
  int getLastImage(long*) {
    ++image_calls;
    return (fail_image_at==image_calls) ? -1 : image_error;
  }
  int getNextImage(long *data) { return getLastImage(data); }
};
Camicaz camera;
struct camicaz_struct { void *camera; } handle = { &camera };
int yCamicaz;
long data_storage[32],argument=2;
void *yget_obj(int, int*) { return &handle; }
long ygets_l(int) { return argument; }
long *ypush_l(long*) { return data_storage; }
void ypush_int(int) {}
void ypush_long(long) {}
void y_error(const char *message) { throw runtime_error(message); }
'''
for name in ("setExpo", "setLatency", "setFilter", "setParam", "setChopping"):
    code += extract(library, "int", "Camicaz::" + name)
for name in ("get_image", "get_next_image", "get_cube", "set_chopping", "set_param"):
    code += extract(wrapper, "void", "Y_yCamicaz_" + name)
code += r'''
void expect_error(void (*operation)(int), int argc) {
  bool failed=false;
  try { operation(argc); } catch (const runtime_error&) { failed=true; }
  assert(failed);
}
int main() {
  Y_yCamicaz_get_image(1);
  Y_yCamicaz_get_next_image(1);
  Y_yCamicaz_get_cube(2);
  camera.image_error=-1;
  expect_error(Y_yCamicaz_get_image,1);
  expect_error(Y_yCamicaz_get_next_image,1);
  expect_error(Y_yCamicaz_get_cube,2);
  camera.image_error=0; camera.image_calls=0; camera.fail_image_at=2;
  expect_error(Y_yCamicaz_get_cube,2);
  assert(camera.image_calls==2);
  camera.fail_image_at=0;
  camera.serial_error=-2; camera.serial_calls=0;
  expect_error(Y_yCamicaz_set_param,4);
  assert(camera.serial_calls==1 && camera.expo==0);
  assert(camera.setLatency(1)<0 && camera.latency==0);
  assert(camera.setFilter(1)<0 && camera.filter==0);
  camera.serial_error=0;
  for (camera.serial_fail_at=2; camera.serial_fail_at<=3; ++camera.serial_fail_at) {
    camera.serial_calls=0;
    expect_error(Y_yCamicaz_set_param,4);
    assert(camera.serial_calls==camera.serial_fail_at);
  }
  camera.serial_fail_at=0;
  Y_yCamicaz_set_param(4);
  assert(camera.expo==2 && camera.latency==2 && camera.filter==2);
  argument=1;
  Y_yCamicaz_set_chopping(2);
  assert(line_status & TIOCM_DTR);
  argument=0;
  Y_yCamicaz_set_chopping(2);
  assert(!(line_status & TIOCM_DTR));
  for (fail_ioctl=TIOCMGET; fail_ioctl<=TIOCMSET; ++fail_ioctl)
    expect_error(Y_yCamicaz_set_chopping,2);
  fail_ioctl=0; camera.serialFdChopping=0;
  expect_error(Y_yCamicaz_set_chopping,2);
  camera.serialFdChopping=1; camera.camAcquire=true; camera.camOpen=false;
  expect_error(Y_yCamicaz_set_chopping,2);
  cout << "PASS C++98: acquisition, serial parameter and DTR error propagation" << endl;
}
'''
with tempfile.TemporaryDirectory(prefix="spydr-camera-errors-") as folder:
    source, binary = Path(folder) / "check.cpp", Path(folder) / "check"
    source.write_text(code)
    subprocess.run(["g++", "-std=gnu++98", "-Wall", "-Wextra", str(source),
                    "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=10)
