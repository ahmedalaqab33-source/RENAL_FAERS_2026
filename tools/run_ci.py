"""Run only local synthetic engineering checks; never a hosted-CI attestation."""
from pathlib import Path
import argparse,csv,decimal,hashlib,importlib.util,json,math,os,re,shutil,signal,subprocess,sys,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ci_qc',ROOT/'tools/release_qc.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
def read(f):
    with f.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def write(f,rows):
    with f.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def equal(a,b,count=False):
    missing=lambda x:x is None or x in ('','NA')
    if missing(a) or missing(b):return missing(a)==missing(b)
    return decimal.Decimal(str(a))==decimal.Decimal(str(b)) if count else math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12)
def external(path):return path!=ROOT and ROOT not in path.parents and path not in ROOT.parents
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);parser.add_argument('--work-dir',required=True);parser.add_argument('--rscript',default='Rscript');parser.add_argument('--command-timeout',type=int,default=180)
    args=parser.parse_args();out=Path(args.output).resolve();work=Path(args.work_dir).resolve()
    try:
        if not 1<=args.command_timeout<=300:raise ValueError('Command timeout must be1..300seconds')
        if not external(out) or out.exists() or not out.parent.is_dir():raise ValueError('New external output with existing parent required')
        if not external(work) or not work.is_dir() or os.name=='nt' and ' ' in str(work):raise ValueError('Explicit external work parent required; Windows R needs no spaces')
        rscript=shutil.which(args.rscript)
        if not rscript:raise ValueError('Rscript is mandatory and unavailable')
        q.verify_manifest(ROOT,ROOT/'RELEASE_MANIFEST.csv')
        if q.scan(ROOT):raise ValueError('Component content screen failed')
        before={f.relative_to(ROOT).as_posix():q.digest(f) for f in ROOT.rglob('*') if f.is_file()}
        if shutil.disk_usage(work).free<268435456:raise ValueError('At least256MiB scratch disk reserve required')
        out.mkdir();(out/'logs').mkdir();cwd=out/'unrelated cwd with spaces';cwd.mkdir();commands=[];start=time.monotonic()
        env=os.environ.copy();env.update(LC_ALL='C',LANG='C',TZ='UTC',TEMP=str(work),TMP=str(work),TMPDIR=str(work),PYTHONDONTWRITEBYTECODE='1')
        def execute(label,cmd,expected_tests=None):
            if time.monotonic()-start>1000 or shutil.disk_usage(work).free<268435456:raise RuntimeError('Total budget or disk reserve reached')
            begin=time.monotonic();kw={'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP} if os.name=='nt' else {'start_new_session':True}
            proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,**kw)
            try:text,_=proc.communicate(timeout=min(args.command_timeout,max(1,1000-(time.monotonic()-start))))
            except subprocess.TimeoutExpired:
                if os.name=='nt':subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
                else:os.killpg(proc.pid,signal.SIGKILL)
                proc.communicate();raise RuntimeError('Synthetic command timeout: '+label)
            (out/'logs'/(label+'.log')).write_text(text,encoding='utf-8');testcount=None
            if expected_tests is not None:
                m=re.search(r'Ran (\d+) tests?',text);testcount=int(m.group(1)) if m else None
            commands.append(dict(label=label,command=cmd,returncode=proc.returncode,seconds=round(time.monotonic()-begin,4),tests=testcount));(out/'executed_commands.json').write_text(json.dumps(commands,indent=2))
            if proc.returncode or expected_tests is not None and testcount!=expected_tests:raise RuntimeError('Synthetic check failed: '+label)
            print(label+': PASS_SCOPED')
            return text
        py=sys.executable
        execute('python_old',[py,'-I',str(ROOT/'tests/run_tests.py')],13)
        execute('r_old',[rscript,'--vanilla',str(ROOT/'tests/run_r_tests.R'),str(ROOT),str(out/'r_old.csv')])
        execute('python_contract',[py,'-I',str(ROOT/'tests/run_contract_tests.py'),str(out/'python_cases.csv')],90)
        execute('r_contract',[rscript,'--vanilla',str(ROOT/'tests/run_contract_tests.R'),str(ROOT),str(out/'r_cases.csv'),str(out/'r_session.txt')])
        execute('runner',[py,'-I',str(ROOT/'tests/run_runner_tests.py'),'--rscript',rscript],36)
        execute('ci_guards',[py,'-I',str(ROOT/'tests/run_ci_guard_tests.py')],8)
        comparisons=[]
        fixture=read(ROOT/'fixtures/synthetic_counts.csv');rold=read(out/'r_old.csv');assert len(fixture)==len(rold)==3
        for x,y in zip(fixture,rold):
            assert x['synthetic_id']==y['synthetic_id'];v=q.metrics(*(int(x[k]) for k in ['a','b','c','d']))
            for k in ['N','ROR','PRR','LCL','UCL']:comparisons.append(dict(category='old_metric',id=x['synthetic_id'],check=k,passed=equal(v[k],y[k],k=='N')))
        pc={x['case_id']:x for x in read(out/'python_cases.csv')};rc={x['case_id']:x for x in read(out/'r_cases.csv')};assert pc.keys()==rc.keys() and len(pc)==89
        for id,x in pc.items():
            y=rc[id];comparisons.append(dict(category='new_classification',id=id,check='acceptance',passed=x['actual']==y['actual']==x['expected']==y['expected']))
            if x['actual']=='ACCEPT':
                for k in ['N','ROR','PRR','LCL','UCL']:comparisons.append(dict(category='new_output',id=id,check=k,passed=equal(x[k],y[k],k=='N')))
        write(out/'parity_checks.csv',comparisons)
        if not all(x['passed'] for x in comparisons):raise RuntimeError('Cross-language parity failure')
        for name in ['demo_a','demo_b']:execute(name,[py,'-I',str(ROOT/'run_demo.py'),'--output',str(out/name),'--work-dir',str(work),'--rscript',rscript])
        products={x.name:q.digest(x) for x in (out/'demo_a').iterdir()};other={x.name:q.digest(x) for x in (out/'demo_b').iterdir()}
        if products!=other or len(products)!=3:raise RuntimeError('Repeated output bytes differ')
        execute('manifest',[py,'-I',str(ROOT/'tools/verify_candidate.py'),str(ROOT)])
        after={f.relative_to(ROOT).as_posix():q.digest(f) for f in ROOT.rglob('*') if f.is_file()}
        if before!=after:raise RuntimeError('Source bytes changed during tests')
        version=execute('r_version',[rscript,'--version']).strip().splitlines()[0]
        summary=dict(scope='SYNTHETIC ENGINEERING ONLY; not hosted-run or scientific attestation',status='PASS_SCOPED',python_version=sys.version.split()[0],r_version=version,old_python_tests=13,new_python_tests=90,new_R_cases=89,runner_tests=36,ci_guard_tests=8,old_metric_checks=15,new_classification_checks=89,new_output_checks=40,repeat_output_hash_checks=3,failures=0,source_manifest_checks='PASS_SCOPED',outputs_uploaded=False)
        (out/'CI_SUMMARY.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n');print(json.dumps(summary,sort_keys=True));return 0
    except (ValueError,RuntimeError,OSError,AssertionError,csv.Error) as e:print('SYNTHETIC_CI_ERROR: '+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
