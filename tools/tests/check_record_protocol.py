"""Exercise the actual Python/Yorick wire callback with the historical C parser.

Run on Linux/WSL; compiles the retained Yorick funcdef.c in an isolated plugin.
No NI driver or camera is loaded. Modern Yorick accepts keyword syntax that
Yorick 2.2.02x silently rejects, so direct calls alone miss this regression.
"""
from pathlib import Path
import argparse
import json
import subprocess
import tempfile
import textwrap
from check_freerun import extract

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--bundle', type=Path)
args = parser.parse_args()
SOURCE = (args.bundle / 'yCamicaz/yorick/spydr' if args.bundle else
          ROOT / 'PC TP IR/TP_Master_version/yCamicaz/yorick/spydr')
LEGACY = ROOT / 'PC TP IR/yorick.git'
with tempfile.TemporaryDirectory(prefix='spydr-wire-') as tmp:
    folder = Path(tmp)
    old = (LEGACY / 'yorick/funcdef.c').read_text()
    old = old.replace('Y_funcdef', 'Y_legacy_funcdef').replace('ypush_func', 'legacy_ypush_func')
    old = old.replace('extern BuiltIn Y_legacy_funcdef;', 'extern BuiltIn Y_legacy_funcdef;\nint legacy_ypush_func(char *);')
    (folder / 'legacy.c').write_text(old)
    (folder / 'wrapper.c').write_text('''
#include "play.h"
#include "ydata.h"
extern BuiltIn Y_legacy_funcdef;
static char *includes[]={0};
static BuiltIn *routines[]={&Y_legacy_funcdef,0};
static void *values[]={0};
static char *names[]={"legacy_funcdef",0};
PLUG_EXPORT char *yk_testwire(char ***,BuiltIn ***,void ***,char ***);
char *yk_testwire(char ***inc,BuiltIn ***code,void ***data,char ***vars) {
  *inc=includes; *code=routines; *data=values; *vars=names;
  return "testwire";
}
''')
    subprocess.run(['gcc', '-fPIC', '-shared', '-I', str(LEGACY/'relocate/include'),
                    str(folder/'legacy.c'), str(folder/'wrapper.c'),
                    '-o', str(folder/'testwire.so')], check=True)
    code = 'plug_dir,_(' + json.dumps(str(folder)) + ',plug_dir());\nplug_in,"testwire";\n'
    code += '''
func check(ok,message) { if (!ok) error,message; }
func probe(a,b=) { extern calls; calls++; }
calls=0;
f=legacy_funcdef("probe 1"); check,is_func(f),"legacy positional command rejected";
f; check,calls==1,"legacy positional command not executed";
f=legacy_funcdef("probe 1, b=2");
check,is_void(f),"historical keyword rejection was not reproduced";
// Run the production callback against the actual retained historical C parser.
funcdef=legacy_funcdef;
_spydr_pyk_linebuf=string(0); pyk_debug=0;
func record_image(typed,obj,n,fold,seq,exp,lat,filt,observer=,notes=,metadata=,focal=,version=,apply_first=) {
  extern calls;
  calls++;
  check,typed==1 && obj=="Target" && n==2 && seq==-1,"positional acquisition settings changed";
  check,fold=="/tmp/night 1" && exp==2 && lat==1 && filt==3,"path or camera settings changed";
  check,strlen(observer)==strlen(expected_observer) && strlen(notes)==strlen(expected_notes),"summary length changed";
  if (strlen(expected_observer)) check,observer==expected_observer,"observer changed";
  if (strlen(expected_notes)) check,notes==expected_notes,"notes changed";
  check,strlen(metadata)==strlen(expected_payload),"metadata length changed";
  if (strlen(expected_payload)) check,metadata==expected_payload,"metadata content changed";
  check,focal==10000. && version=="test","focal length or version changed";
  check,apply_first==expected_apply,"Apply flag changed";
}
'''
    backend=(SOURCE/'spydr_widgetcam.i').read_text()
    code += extract(backend,'func','cam_record_request')+'\n'
    code += extract((SOURCE/'spydr_pyk.i').read_text(),'func','_spydr_pyk_callback')+'\n'
    # Extract the real Python command template, rather than retyping it here.
    python=(SOURCE/'spydr.py').read_text()
    start=python.index('      self._pending_record_command = (')
    end=python.index('      self._pending_record_params = ',start)
    build=textwrap.dedent(python[start:end])
    from types import SimpleNamespace
    cases=0
    for length in (0,80,337,4096):
        payload='A'*length
        gui=SimpleNamespace(spydr_version='test')
        observer='' if length==0 else 'Observer'
        notes='' if length==0 else 'Notes with \"quotes\" and \\ path'
        def quoted(value):
            return '@'+value.replace('\\','\\\\').replace('"','\\"')
        values=dict(self=gui,typed=1,objectd='Target',nb_images=2,fold='/tmp/night 1',
                    seqid=-1,exp=2,lat=1,filt=3,observer=observer,notes=notes,
                    payload='@'+payload,focal=10000.,summary=lambda x:x,quoted=quoted)
        exec(build,values)
        for apply in (0,1):
            command=gui._pending_record_command+' %d'%apply
            assert '\n' not in command and ', observer=' not in command
            code+='expected_observer='+json.dumps(observer)+'; expected_notes='+json.dumps(notes)+';\n'
            code+='expected_payload='+json.dumps(payload)+'; expected_apply=%d;\n'%apply
            # Whole line, fragmented line, and two commands delivered together.
            code+='_spydr_pyk_callback,'+json.dumps(command+'\n')+';\n'
            code+='check,calls==%d,"whole command dropped";\n'%(cases+2);cases+=1
            for chunk in (command[:23],command[23:]+'\n'):
                code+='_spydr_pyk_callback,'+json.dumps(chunk)+';\n'
            code+='check,calls==%d,"fragmented command dropped";\n'%(cases+2);cases+=1
            code+='_spydr_pyk_callback,'+json.dumps(command+'\n'+command+'\n')+';\n'
            cases+=2
            code+='check,calls==%d,"batched commands dropped";\n'%(cases+1)
    code+='write,"PASS historical Record protocol: keyword failure reproduced; %d positional commands, fragmented/batched transport, metadata and Apply preserved";\nquit;\n'%cases
    (folder/'check.i').write_text(code)
    run=subprocess.run(['yorick','-batch',str(folder/'check.i')],capture_output=True,text=True,timeout=20)
    print(run.stdout+run.stderr)
    assert run.returncode==0 and 'PASS historical Record protocol' in run.stdout
