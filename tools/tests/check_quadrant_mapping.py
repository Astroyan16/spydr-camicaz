"""Compile the real quadrant reconstruction and check every pixel of both reads."""
from pathlib import Path
import subprocess
import tempfile

from check_freerun import extract


ROOT = Path(__file__).resolve().parents[2] / "PC TP IR/TP_Master_version"
source = (ROOT / "libcamicaz/src/camicaz.cpp").read_text()
code = r'''
#include <algorithm>
#include <cassert>
#include <iostream>
#include <vector>
#include <unistd.h>
using namespace std;
typedef int int32;
typedef unsigned int uInt32;
class Camicaz {
public:
  bool camOpen,camAcquire,newFrame,camGetImage;
  long size,dims[3];
  uInt32 *lastFrame;
  int32 error;
  int32 getLastImage(long*);
};
'''
code += extract(source, "int32", "Camicaz::getLastImage")
code += r'''
bool check_frame(int side, int planes) {
  const long plane_size=side*side, total=plane_size*planes;
  Camicaz camera;
  camera.camOpen=true; camera.camAcquire=false;
  camera.newFrame=true; camera.camGetImage=false;
  camera.dims[0]=camera.dims[1]=side; camera.dims[2]=planes;
  camera.size=total; camera.error=0;
  vector<uInt32> raw(total);
  vector<long> expected(total,-1), actual(total+2,-999), occurrences(total,0);
  long sample=0;
  // Preserve historical amplifier order: upper-right, lower-right, lower-left,
  // upper-left. Absolute detector orientation still needs a hardware reference.
  for (int plane=0;plane<planes;plane++) {
    for (int row=0;row<side/2;row++) {
      for (int col=0;col<side/2;col++) {
        for (int quadrant=0;quadrant<4;quadrant++) {
          long value=plane*plane_size+quadrant*(plane_size/4)+row*(side/2)+col+1;
          int out_row=row+((quadrant==1 || quadrant==2) ? side/2 : 0);
          int out_col=col+((quadrant==0 || quadrant==1) ? side/2 : 0);
          raw[sample++]=value;
          expected[plane*plane_size+out_row*side+out_col]=value;
        }
      }
    }
  }
  camera.lastFrame=&raw[0];
  assert(camera.getLastImage(&actual[1])==0);
  assert(actual.front()==-999 && actual.back()==-999);
  long missing=0,mismatched=0;
  for (long pixel=0;pixel<total;pixel++) {
    long value=actual[pixel+1];
    if (value==-999) missing++;
    if (value!=expected[pixel]) mismatched++;
    if (value>0 && value<=total) occurrences[value-1]++;
  }
  if (missing || mismatched) {
    cerr << side << "x" << side << "x" << planes
         << ": unfilled=" << missing << ", mismatched=" << mismatched << endl;
    return false;
  }
  for (long value=0;value<total;value++) assert(occurrences[value]==1);
  assert(!camera.newFrame && !camera.camGetImage);
  return true;
}
int main() {
  bool ok=check_frame(256,2);
  ok=check_frame(256,1) && ok;
  ok=check_frame(8,2) && ok;
  if (!ok) return 1;
  cout << "PASS quadrant mapping: all pixels, read separation, seams and memory guards" << endl;
}
'''
with tempfile.TemporaryDirectory(prefix="spydr-quadrants-") as folder:
    source_file, binary = Path(folder) / "check.cpp", Path(folder) / "check"
    source_file.write_text(code)
    subprocess.run(["g++", "-std=gnu++98", "-Wall", "-Wextra", str(source_file),
                    "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=10)
