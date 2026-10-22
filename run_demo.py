"""Portable, manifest-bound SYNTHETIC / NOT FAERS engineering demonstration."""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,io,json,math,os,re,shutil,subprocess,sys,tempfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('component_qc',ROOT/'tools/release_qc.py')
qc=importlib.util.module_from_spec(spec);spec.loader.exec_module(qc)
FIXTURES=('demo_counts.csv','synthetic_counts.csv')
FIELDS=['synthetic_id','a','b','c','d']
LABEL='SYNTHETIC / NOT FAERS'
class DemoError(Exception):
    def __init__(self,message,code=2):super().__init__(message);self.code=code
def read_fixture(name):
    f=ROOT/'fixtures'/name
    if f.is_symlink() or not f.is_file() or f.stat().st_size>16384:raise DemoError('Invalid bounded synthetic fixture')
    with f.open(encoding='utf-8-sig',newline='') as h:
        reader=csv.DictReader(h)
        if reader.fieldnames!=FIELDS:raise DemoError('Fixture header must be synthetic_id,a,b,c,d')
        rows=[];seen=set()
        for row in reader:
            if len(rows)>=32 or set(row)!=set(FIELDS) or any(x is None for x in row.values()):raise DemoError('Invalid fixture shape or row limit')
            sid=row['synthetic_id']
            if not re.fullmatch(r'SYNTHETIC_[A-Z0-9_]{1,48}',sid) or sid in seen:raise DemoError('Expected unique artificial SYNTHETIC labels')
            seen.add(sid);cells=[]
            for k in FIELDS[1:]:
                token=row[k]
                if not re.fullmatch(r'0|[1-9][0-9]{0,15}',token):raise DemoError('Cells require canonical decimal integer tokens; no logical,missing or coercion')
                cells.append(int(token))
            try:metrics=qc.metrics(*cells)
            except ValueError:raise DemoError('Count or table total outside strict contract') from None
            rows.append((sid,metrics))
    if not rows:raise DemoError('Synthetic fixture must have at least one row')
    return f,rows
def csv_bytes(headers,rows):
    text=io.StringIO(newline='');w=csv.writer(text,lineterminator='\n');w.writerow(headers);w.writerows(rows);return text.getvalue().encode('utf-8')
def numeric_string(x):return 'UNDEFINED' if x is None else format(x,'.17g')
def execute(args):
    # Validate the exact component before any fixture read or output creation.
    try:qc.verify_manifest(ROOT,ROOT/'RELEASE_MANIFEST.csv')
    except (ValueError,OSError,KeyError):raise DemoError('Component manifest verification failed') from None
    fixture,rows=read_fixture(args.fixture)
    destination=Path(args.output).expanduser().resolve()
    if destination==ROOT or ROOT in destination.parents or destination in ROOT.parents:raise DemoError('Output must be outside the component and its ancestors')
    if destination.exists():raise DemoError('Output directory must be new; overwrite is disabled')
    if not destination.parent.is_dir():raise DemoError('Output parent directory must already exist')
    rscript=shutil.which(args.rscript)
    if not rscript:raise DemoError('Rscript unavailable; supply --rscript with an installed executable')
    workroot=Path(args.work_dir).expanduser().resolve() if args.work_dir else destination
    if args.work_dir:
        if not workroot.is_dir() or workroot==ROOT or ROOT in workroot.parents or workroot in ROOT.parents:raise DemoError('Work directory must be an existing external temporary directory')
    if os.name=='nt' and ' ' in str(workroot):raise DemoError('Windows R requires a no-space temporary path; explicitly supply --work-dir')
    destination.mkdir()
    with tempfile.TemporaryDirectory(prefix='.synthetic_work_',dir=workroot) as tmp:
        temp=Path(tmp);rout=temp/'r_results.csv';env=os.environ.copy();env.update(LC_ALL='C',LANG='C',TEMP=str(temp),TMP=str(temp),TMPDIR=str(temp))
        try:
            result=subprocess.run([rscript,'--vanilla',str(ROOT/'R/run_fixture.R'),args.fixture,str(rout)],cwd=temp,env=env,capture_output=True,text=True,timeout=60)
        except (OSError,subprocess.TimeoutExpired):raise DemoError('R worker could not complete',3) from None
        if result.returncode!=0 or not rout.is_file():raise DemoError('R worker failed; no successful demonstration output',3)
        with rout.open(encoding='utf-8-sig',newline='') as h:rrows=list(csv.DictReader(h))
        if len(rrows)!=len(rows):raise DemoError('R/Python row conservation mismatch',4)
        comparisons=0
        for (sid,py),r in zip(rows,rrows):
            if r.get('synthetic_id')!=sid or r.get('state')!=py['state']:raise DemoError('R/Python identity or undefined-state mismatch',4)
            for k in ['N','ROR','PRR','LCL','UCL']:
                rv=r.get(k)
                if py[k] is None:
                    if rv!='UNDEFINED':raise DemoError('R/Python undefined-state mismatch',4)
                elif k=='N':
                    if not rv or not rv.isdigit() or int(rv)!=py[k]:raise DemoError('R/Python exact count mismatch',4)
                else:
                    try:ok=math.isfinite(float(rv)) and math.isclose(py[k],float(rv),rel_tol=1e-12,abs_tol=1e-12)
                    except (ValueError,TypeError):ok=False
                    if not ok:raise DemoError('R/Python numeric parity mismatch',4)
                comparisons+=1
        outputrows=[]
        for sid,v in rows:outputrows.append([sid,LABEL,str(int(v['N']))]+[numeric_string(v[k]) for k in ['ROR','PRR','LCL','UCL']]+[v['state']])
        data=csv_bytes(['synthetic_id','dataset_label','N','ROR','PRR','LCL','UCL','state'],outputrows)
        summary=dict(dataset_label=LABEL,fixture=args.fixture,fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),schema_version=1,rows=len(rows),undefined_rows=sum(v['state']=='UNDEFINED' for _,v in rows),numeric_parity_checks=comparisons,status='PASS_SCOPED',scope='Synthetic engineering arithmetic; no scientific validation')
        products={'synthetic_results.csv':data,'summary.json':(json.dumps(summary,sort_keys=True,indent=2)+'\n').encode('utf-8')}
        manifest=csv_bytes(['path','sha256','bytes'],[[name,hashlib.sha256(payload).hexdigest(),len(payload)] for name,payload in sorted(products.items())])
        products['OUTPUT_MANIFEST.csv']=manifest
        # Stage final bytes on the output volume even if the explicit work root differs.
        for name,payload in products.items():
            with tempfile.NamedTemporaryFile(prefix='.synthetic_output_',dir=destination,delete=False) as h:h.write(payload);pending=Path(h.name)
            os.replace(pending,destination/name)
    print('SYNTHETIC / NOT FAERS: PASS_SCOPED')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture',choices=FIXTURES,default='demo_counts.csv',help='Bundled manifest-bound fixture name only')
    parser.add_argument('--output',required=True,help='New directory outside the component; parent must exist')
    parser.add_argument('--rscript',default='Rscript',help='Installed Rscript executable or PATH command; R is mandatory')
    parser.add_argument('--work-dir',help='Optional existing external temporary parent; explicitly required for Windows output paths with spaces')
    args=parser.parse_args()
    try:execute(args)
    except DemoError as error:print('SYNTHETIC_DEMO_ERROR: '+str(error),file=sys.stderr);return error.code
    except (OSError,UnicodeError,csv.Error):print('SYNTHETIC_DEMO_ERROR: input/output encoding or access failure',file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
