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
parser.add_argument('--docs-ref',help='Documentation revision (default HEAD); runtime files always come from --ref')
parser.add_argument('--launchers-ref',help='Launcher revision (default --ref); acquisition sources stay pinned')
parser.add_argument('--launcher-validation-report',type=Path)
parser.add_argument('--revision',default='',help='Packaging suffix, e.g. r2; does not change the software version')
parser.add_argument('--validation-report',type=Path)
args=parser.parse_args()
def git(*cmd):return subprocess.check_output(['git',*cmd],cwd=ROOT)
commit=git('rev-parse',args.ref+'^{commit}').decode().strip()
docs_commit=git('rev-parse',(args.docs_ref or 'HEAD')+'^{commit}').decode().strip()
launchers_commit=git('rev-parse',(args.launchers_ref or args.ref)+'^{commit}').decode().strip()
if args.revision and not args.revision.isalnum():raise ValueError('Invalid packaging revision')
prefix='PC TP IR/TP_Master_version/'
version=git('show',commit+':'+prefix+'yCamicaz/yorick/spydr/VERSION').decode().strip()
if not version or any(c not in '0123456789.ab' for c in version):raise ValueError('Invalid version')
out=args.output.resolve()
out.mkdir(parents=True,exist_ok=False)
name='spydr_camicaz_'+version+'_release'+('-'+args.revision if args.revision else '')
bundle=out/name;bundle.mkdir()
paths=[prefix+'libcamicaz',prefix+'yCamicaz']
raw=git('archive','--format=zip',commit,'--',*paths)
items={};manifest=[]
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 for item in z.infolist():
  if item.is_dir():continue
  path=PurePosixPath(item.filename)
  if item.filename.startswith(prefix):dest=item.filename[len(prefix):]
  else:continue
  if any(part in ('.git','.svn','__pycache__','obj') for part in path.parts):raise ValueError('Unexpected metadata/build directory')
  if path.suffix.lower() in ('.so','.o','.obj','.pyc','.dll','.exe','.log'):raise ValueError('Unexpected binary or runtime file')
  if dest in items:raise ValueError('Duplicate destination: '+dest)
  data=z.read(item)
  items[dest]=data
  manifest.append(dict(path=dest,git_path=item.filename,git_commit=commit,sha256=hashlib.sha256(data).hexdigest()))
for name in ('run_spydr_test.sh','rebuild_with_existing_yorick.sh'):
 source='tools/spydr-system-yorick/'+name
 data=git('show',launchers_commit+':'+source)
 items[name]=data
 manifest.append(dict(path=name,git_path=source,git_commit=launchers_commit,sha256=hashlib.sha256(data).hexdigest()))
# Keep the delivered guide small; historical fix notes stay in the repository.
for source,dest in (('README_RELEASE.md','README.md'),('docs/FITS_METADATA.md','docs/FITS_METADATA.md')):
 data=git('show',docs_commit+':'+source)
 items[dest]=data
 manifest.append(dict(path=dest,git_path=source,git_commit=docs_commit,sha256=hashlib.sha256(data).hexdigest()))
assert 'yCamicaz/yorick/spydr/spydr_metadata.i' in items
assert all('yCamicaz/yorick/spydr/spydr-doux-%d.png'%n in items for n in (16,32,48,128))
if args.validation_report:
 checks=json.loads(args.validation_report.read_text())
 assert checks and all(r['passed'] for r in checks)
 items['docs/verification/VALIDATION.json']=(json.dumps(dict(source_commit=commit,checks=checks),indent=2)+'\n').encode()
if args.launcher_validation_report:
 checks=json.loads(args.launcher_validation_report.read_text())
 assert checks and checks['passed']
 items['docs/verification/LAUNCHER_CHECKS.json']=(json.dumps(dict(launcher_commit=launchers_commit,checks=checks),indent=2)+'\n').encode()
items['docs/verification/MANIFEST.json']=(json.dumps(dict(version=version,source_commit=commit,documentation_commit=docs_commit,launcher_commit=launchers_commit,packaging_revision=args.revision or 'initial',files=manifest),indent=2)+'\n').encode()
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
(out/('SHA256SUMS'+('-'+args.revision if args.revision else '')+'.txt')).write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in (zip_path,tar_path)))
print('Source commit:',commit)
print('Verified files:',len(manifest))
print('ZIP:',zip_path)
print('TAR:',tar_path)
