"""Exercise launcher/build preflight in disposable Linux fixtures, without NI."""
from pathlib import Path
import argparse,json,os,subprocess,tempfile,unittest

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--bundle',type=Path)
parser.add_argument('--report',type=Path)
args=parser.parse_args()
SOURCE=args.bundle or ROOT/'tools/spydr-system-yorick'

class LauncherTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='spydr-launcher-')
  self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  for d in ('libcamicaz','yCamicaz/yorick/spydr','fake-yorick/bin','commands'):(self.root/d).mkdir(parents=True)
  for name in ('run_spydr_test.sh','rebuild_with_existing_yorick.sh'):
   (self.root/name).write_text((SOURCE/name).read_text())
  (self.root/'yCamicaz/yorick/spydr/VERSION').write_text('0.9.8b\n')
  (self.root/'fake-yorick/Make.cfg').write_text('# test fixture\n')
  self.executable('fake-yorick/bin/yorick','#!/bin/sh\nprintf "YORICK_STARTED\\n"\n')
  self.executable('commands/rlwrap','#!/bin/sh\nexec "$@"\n')
  self.executable('commands/g++','#!/bin/sh\nexit 0\n')
  self.executable('commands/make','''#!/usr/bin/python3
from pathlib import Path
import os,sys
p=Path(sys.argv[sys.argv.index('-C')+1]); mode=os.environ['BUILD_MODE']
with open(os.environ['MAKE_LOG'],'a') as log:log.write(str(p)+' '+repr(sys.argv[1:])+'\\n')
if 'clean' in sys.argv:sys.exit(0)
if mode=='make_fails':sys.exit(7)
lib='libcamicaz.so' if p.name=='libcamicaz' else 'yCamicaz.so'
kind='lib' if p.name=='libcamicaz' else 'ycam'
if mode=='missing_'+kind:sys.exit(0)
(p/lib).write_bytes(b'' if mode=='empty_'+kind else b'test fixture, not a real library')
''')
  self.env=dict(os.environ,PATH=str(self.root/'commands')+':'+os.environ['PATH'],
   SPYDR_TEST_YORICK_BIN=str(self.root/'fake-yorick/bin/yorick'),
   SPYDR_TEST_YORICK_ROOT=str(self.root/'fake-yorick'),MAKE_LOG=str(self.root/'make.log'))
 def executable(self,name,text):
  p=self.root/name;p.write_text(text);p.chmod(0o755)
 def run_script(self,name,**env):
  return subprocess.run(['sh',str(self.root/name)],capture_output=True,text=True,env=dict(self.env,**env),timeout=10)
 def test_launch_rejects_missing_and_empty_libraries(self):
  libs=[self.root/'libcamicaz/libcamicaz.so',self.root/'yCamicaz/yCamicaz.so']
  for values in ((None,None),(b'',b'fixture'),(b'fixture',b'')):
   with self.subTest(values=values):
    for p,value in zip(libs,values):
     if value is not None:p.write_bytes(value)
    r=self.run_script('run_spydr_test.sh')
    self.assertNotEqual(r.returncode,0)
    self.assertIn('missing or empty',r.stderr)
    self.assertNotIn('YORICK_STARTED',r.stdout)
 def test_launch_accepts_nonempty_libraries(self):
  for name in ('libcamicaz/libcamicaz.so','yCamicaz/yCamicaz.so'):(self.root/name).write_bytes(b'fixture')
  r=self.run_script('run_spydr_test.sh')
  self.assertEqual(r.returncode,0,r.stderr)
  self.assertIn('YORICK_STARTED',r.stdout)
 def test_build_rejects_missing_and_empty_outputs(self):
  for mode in ('missing_lib','empty_lib','missing_ycam','empty_ycam','make_fails'):
   with self.subTest(mode=mode):
    for p in (self.root/'libcamicaz/libcamicaz.so',self.root/'yCamicaz/yCamicaz.so'):
     if p.exists():p.unlink()
    r=self.run_script('rebuild_with_existing_yorick.sh',BUILD_MODE=mode)
    self.assertNotEqual(r.returncode,0)
    self.assertNotIn('rebuilt successfully',r.stdout)
    if mode!='make_fails':self.assertIn('missing or empty',r.stderr)
 def test_build_only_announces_success_with_both_outputs(self):
  r=self.run_script('rebuild_with_existing_yorick.sh',BUILD_MODE='ok')
  self.assertEqual(r.returncode,0,r.stdout+r.stderr)
  self.assertIn('Application libraries rebuilt successfully',r.stdout)
  self.assertTrue((self.root/'libcamicaz/libcamicaz.so').stat().st_size)
  self.assertTrue((self.root/'yCamicaz/yCamicaz.so').stat().st_size)

result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(LauncherTests))
if args.report:
 args.report.write_text(json.dumps(dict(passed=result.wasSuccessful(),tests=result.testsRun,
  cases='missing/empty libraries, no premature launch or build success, compiler failure, successful outputs',
  environment='isolated shell fixtures, no instrument access'),indent=2)+'\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
