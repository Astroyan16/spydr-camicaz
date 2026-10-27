"""Check shell-free UTC formatting against Python's UTC calendar and benchmark it.

Run with Python on Windows (uses WSL Yorick) or Linux. No camera or NI driver.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import json
import math
import os
import random
import subprocess
import tempfile
from check_freerun import extract

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--bundle',type=Path)
args=parser.parse_args()
source=(args.bundle/'yCamicaz/yorick/spydr' if args.bundle else
        ROOT/'PC TP IR/TP_Master_version/yCamicaz/yorick/spydr')
version=(source/'VERSION').read_text().strip()
fine=version.endswith('b')
formatter=extract((source/'spydr_metadata.i').read_text(),'func','cam_utc')
assert 'popen' not in formatter and 'rdline' not in formatter

def expected(seconds):
    whole=math.floor(seconds)
    micros=math.floor((seconds-whole)*1e6+0.5) if fine else 0
    if micros==1000000:whole+=1;micros=0
    t=datetime(1970,1,1,tzinfo=timezone.utc)+timedelta(seconds=whole)
    text=t.strftime('%Y-%m-%dT%H:%M:%S')
    return text+('.%06dZ'%micros if fine else 'Z')

samples=[-1.,0.,1.,1700000010.,1792685694.744979470,1792685695.403534765,
         0.9999996,86399.9999996,-0.0000004,-0.0000006,2147483647.,2147483648.]
for year in (1900,1968,1970,1999,2000,2004,2026,2038,2100,2400):
    for month,day in ((1,1),(2,28),(3,1),(12,31)):
        t=datetime(year,month,day,tzinfo=timezone.utc).timestamp()
        samples.extend((t-1.,t,t+86399.,t+86399.75))
rng=random.Random(20261022)
for i in range(300):
    t=datetime(1900,1,1,tzinfo=timezone.utc)+timedelta(days=rng.randrange(182000),seconds=rng.randrange(86400))
    samples.append(t.timestamp()+rng.random())
code=formatter+'\nfunc check(ok,message) { if (!ok) error,message; }\n'
for value in samples:
    code+='check,cam_utc(%.17g)==%s,%s;\n'%(value,json.dumps(expected(value)),json.dumps('UTC mismatch at %.17g'%value))
code+='''
t0=array(0.,3); t1=array(0.,3); timer,t0;
for (i=1;i<=10000;i++) result=cam_utc(1792685694.744979470);
timer,t1;
write,format="UTC BENCH %.3f us/conversion (host interpreter, 10000 calls)\\n",(t1(3)-t0(3))*1.e6/10000.;
'''
code+='write,"PASS UTC '+version+': %d dates, leap years, midnight, pre-epoch and 2038 boundaries, fractional rounding";\nquit;\n'%len(samples)
with tempfile.TemporaryDirectory(prefix='spydr-utc-') as tmp:
    path=Path(tmp)/'check.i';path.write_bytes(code.encode())
    if os.name=='nt':
        linux=subprocess.check_output(['wsl','-d','Ubuntu','--','wslpath','-a',path.as_posix()],text=True).strip()
        command=['wsl','-d','Ubuntu','--','env','TZ=Pacific/Honolulu','yorick','-batch',linux]
    else:
        command=['env','TZ=Pacific/Honolulu','yorick','-batch',str(path)]
    run=subprocess.run(command,capture_output=True,text=True,timeout=30)
    print(run.stdout+run.stderr)
    assert run.returncode==0 and 'PASS UTC' in run.stdout
