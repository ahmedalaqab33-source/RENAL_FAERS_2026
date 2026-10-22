"""Execute the single bundled synthetic M1 fixture, with real R/Python validators."""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,tempfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def external(p):return p!=ROOT and ROOT not in p.parents and p not in ROOT.parents
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True);ap.add_argument('--work-dir',required=True);ap.add_argument('--rscript',default='Rscript');a=ap.parse_args()
    try:
        output=Path(a.output).resolve();work=Path(a.work_dir).resolve()
        if not external(output) or output.exists() or not output.parent.is_dir():raise ValueError('New external output required')
        if not external(work) or not work.is_dir() or os.name=='nt' and ' ' in str(work):raise ValueError('External no-space Windows R work parent required')
        rscript=shutil.which(a.rscript)
        if not rscript:raise ValueError('Rscript unavailable')
        qc=load('demo_qc',ROOT/'tools/release_qc.py');qc.verify_manifest(ROOT,ROOT/'RELEASE_MANIFEST.csv')
        validator=load('demo_m1',ROOT/'python/m1_validator.py').validate_sufficient_statistics
        fixture=ROOT/'fixtures/m1_demo.csv'
        with fixture.open(encoding='utf-8',newline='') as f:
            reader=csv.DictReader(f)
            if reader.fieldnames!=['pair_id','a','b','c','d','n_drug','n_event']:raise ValueError('Fixture schema')
            data=[]
            for row in reader:
                if not all(re.fullmatch(r'0|[1-9][0-9]*',row[k] or '') for k in reader.fieldnames[1:]):raise ValueError('Fixture integer syntax')
                data.append(dict(pair_id=row['pair_id'],**{k:int(row[k]) for k in reader.fieldnames[1:]}))
        if not 1<=len(data)<=32 or fixture.stat().st_size>16384:raise ValueError('Fixture bounds')
        answer=validator(data)
        with tempfile.TemporaryDirectory(prefix='m1_demo_',dir=work) as temp:
            rpath=Path(temp)/'r_validation.csv';env=os.environ.copy();env.update(LC_ALL='C',LANG='C',TZ='UTC',TEMP=temp,TMP=temp,TMPDIR=temp)
            r=subprocess.run([rscript,'--vanilla',str(ROOT/'R/run_m1_demo.R'),str(ROOT),str(rpath)],env=env,capture_output=True,text=True,timeout=60)
            if r.returncode:raise ValueError('R worker failed')
            with rpath.open(encoding='utf-8-sig',newline='') as f:observed=list(csv.DictReader(f))
            if len(observed)!=len(data):raise ValueError('R row count')
            for row,other in zip(data,observed):
                if other['pair_id']!=row['pair_id'] or any(int(other[k])!=v for k,v in [('n_drug',row['n_drug']),('n_event',row['n_event']),('N',answer['N'])]):raise ValueError('R/Python mismatch')
        product=dict(scope='SYNTHETIC / NOT FAERS; M1 structural validation only',accepted=answer['accepted'],row_count=answer['row_count'],N=answer['N'],pair_ids=answer['pair_ids'],fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),cross_language_checks=len(data)*4)
        output.mkdir();dest=output/'m1_validation.json';dest.write_text(json.dumps(product,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        with (output/'OUTPUT_MANIFEST.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['path','sha256','bytes']);w.writerow([dest.name,hashlib.sha256(dest.read_bytes()).hexdigest(),dest.stat().st_size])
        print('M1_SYNTHETIC_DEMO_PASS');return 0
    except (ValueError,OSError,KeyError,csv.Error,subprocess.TimeoutExpired):
        print('M1_DEMO_ERROR: input,manifest,path,runtime or parity check failed',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
