"""Verify checkout content and test an exact manifest-only copy, without touching Git metadata."""
from pathlib import Path
import argparse,csv,hashlib,os,shutil,subprocess,sys,tempfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def stage_component(source,dest):
    with (source/'RELEASE_MANIFEST.csv').open(encoding='utf-8-sig',newline='') as h:rows=list(csv.DictReader(h))
    expected=set()
    for row in rows:
        rel=Path(row['path'])
        if rel.is_absolute() or '..' in rel.parts or '\\' in row['path'] or ':' in row['path'] or '.git' in rel.parts or row['path'] in expected:raise ValueError('Unsafe or duplicate manifest path')
        expected.add(row['path']);f=source/rel
        if f.is_symlink() or not f.is_file() or not source.resolve() in f.resolve().parents:raise ValueError('Unsafe manifest source')
        if hashlib.sha256(f.read_bytes()).hexdigest()!=row['sha256'] or f.stat().st_size!=int(row['bytes']):raise ValueError('Source manifest mismatch')
    actual=set()
    for directory,dirs,files in os.walk(source,followlinks=False):
        path=Path(directory)
        if path==source and '.git' in dirs:dirs.remove('.git')
        if any((path/d).is_symlink() for d in dirs):raise ValueError('Symlink directory in component')
        for name in files:
            f=path/name
            if f.is_symlink():raise ValueError('Symlink file in component')
            actual.add(f.relative_to(source).as_posix())
    if actual!=expected|{'RELEASE_MANIFEST.csv'}:raise ValueError('Unlisted checkout content outside top-level Git metadata')
    dest.mkdir()
    for rel in sorted(actual):
        target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/rel,target)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);parser.add_argument('--work-dir',required=True);parser.add_argument('--rscript',default='Rscript');args=parser.parse_args()
    work=Path(args.work_dir).resolve();out=Path(args.output).resolve()
    try:
        if not work.is_dir() or work==ROOT or ROOT in work.parents or work in ROOT.parents or os.name=='nt' and ' ' in str(work):raise ValueError('Explicit external work root required; Windows R needs no spaces')
        if out.exists() or not out.parent.is_dir() or out==ROOT or ROOT in out.parents or out in ROOT.parents:raise ValueError('New external output required')
        if not shutil.which(args.rscript):raise ValueError('Mandatory Rscript unavailable')
        with tempfile.TemporaryDirectory(prefix='synthetic_ci_',dir=work) as tmp:
            component=Path(tmp)/'component with spaces';rwork=Path(tmp)/'r_work';rwork.mkdir();stage_component(ROOT,component)
            return subprocess.run([sys.executable,'-I',str(component/'tools/run_ci.py'),'--output',str(out),'--work-dir',str(rwork),'--rscript',args.rscript],check=False).returncode
    except (ValueError,OSError,KeyError,csv.Error):print('SYNTHETIC_BOOTSTRAP_ERROR: integrity,source scope,path or interpreter check failed',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
