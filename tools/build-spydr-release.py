"""Build isolated source releases from an exact Git revision, using the stdlib."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import subprocess
import tarfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ref',required=True,help='Existing local tag or commit')
parser.add_argument('--output',type=Path,required=True,help='New output directory')
parser.add_argument('--validation-report',type=Path)
args=parser.parse_args()
def git(*cmd):return subprocess.check_output(['git',*cmd],cwd=ROOT)
commit=git('rev-parse',args.ref+'^{commit}').decode().strip()
prefix='PC TP IR/TP_Master_version/'
version=git('show',commit+':'+prefix+'yCamicaz/yorick/spydr/VERSION').decode().strip()
if not version or any(c not in '0123456789.ab' for c in version):raise ValueError('Invalid version')
out=args.output.resolve()
out.mkdir(parents=True,exist_ok=False)
name='spydr_camicaz_'+version+'_release'
bundle=out/name;bundle.mkdir()
paths=[prefix+'libcamicaz',prefix+'yCamicaz','tools/spydr-system-yorick','docs','CHANGELOG.md']
raw=git('archive','--format=zip',commit,'--',*paths)
items={};manifest=[]
release_docs={'FITS_METADATA.md','FOCALE_NICMOS.md','APPLY_AND_RECORD.md','AUTO_STATUS.md',
              'RECORD_PROGRESS.md','RELEASE_'+version+'.md','CORRECTIF_DATES_UTC_20261022.md',
              'CORRECTIF_PROTOCOLE_RECORD_20261022.md'}
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 for item in z.infolist():
  if item.is_dir():continue
  path=PurePosixPath(item.filename)
  if item.filename.startswith(prefix):dest=item.filename[len(prefix):]
  elif item.filename.startswith('tools/spydr-system-yorick/'):dest=path.name
  elif item.filename.startswith('docs/') and path.name in release_docs:dest=path.name
  elif item.filename=='CHANGELOG.md':dest=path.name
  else:continue
  if any(part in ('.git','.svn','__pycache__','obj') for part in path.parts):raise ValueError('Unexpected metadata/build directory')
  if path.suffix.lower() in ('.so','.o','.obj','.pyc','.dll','.exe','.log'):raise ValueError('Unexpected binary or runtime file')
  if dest in items:raise ValueError('Duplicate destination: '+dest)
  data=z.read(item)
  items[dest]=data
  manifest.append(dict(path=dest,git_path=item.filename,sha256=hashlib.sha256(data).hexdigest()))
assert 'yCamicaz/yorick/spydr/spydr_metadata.i' in items
assert all('yCamicaz/yorick/spydr/spydr-doux-%d.png'%n in items for n in (16,32,48,128))
if args.validation_report:
 checks=json.loads(args.validation_report.read_text())
 assert checks and all(r['passed'] for r in checks)
 items['VALIDATION.json']=(json.dumps(dict(source_commit=commit,checks=checks),indent=2)+'\n').encode()
items['MANIFEST.json']=(json.dumps(dict(version=version,source_commit=commit,files=manifest),indent=2)+'\n').encode()
for dest,data in items.items():
 target=bundle/dest
 assert target.resolve().is_relative_to(bundle.resolve())
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
zip_path=out/(name+'.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for dest,data in sorted(items.items()):
  info=zipfile.ZipInfo(name+'/'+dest)
  info.external_attr=((0o100755 if dest.endswith('.sh') else 0o100644)<<16)
  info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,data)
tar_path=out/(name+'.tar.gz')
with tarfile.open(tar_path,'w:gz') as tar:
 for dest,data in sorted(items.items()):
  info=tarfile.TarInfo(name+'/'+dest);info.size=len(data)
  info.mode=0o755 if dest.endswith('.sh') else 0o644
  tar.addfile(info,io.BytesIO(data))
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 for dest,data in items.items():assert z.read(name+'/'+dest)==data
with tarfile.open(tar_path,'r:gz') as tar:
 for dest,data in items.items():assert tar.extractfile(name+'/'+dest).read()==data
(out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in (zip_path,tar_path)))
print('Source commit:',commit)
print('Verified files:',len(manifest))
print('ZIP:',zip_path)
print('TAR:',tar_path)
