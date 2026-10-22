"""Synthetic-only M1 regression coordinator; functions themselves perform no IO."""
from pathlib import Path
import argparse,csv,decimal,importlib.util,json,os,subprocess,sys,math,re,copy,ast,builtins,socket,hashlib,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
FIELDS=['pair_id','a','b','c','d','n_drug','n_event']
def read(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
    with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def decode(token):
    kind,value=token.split(':',1)
    if kind=='s':return value
    if kind=='n':return int(value)
    if kind=='f':return float(value)
    if kind=='b':return value=='true'
    if kind=='nl':return value+'\n'
    if kind=='cr':return value+'\r'
    if kind=='null':return None
    if kind=='na':return float('nan')
    return {'nan':float('nan'),'inf':float('inf'),'neginf':-float('inf')}[kind]
class HostileString(str):pass
def build(d):
    if d['variant']=='empty':return []
    rows=[dict(zip(FIELDS,[decode(t) for t in line.split(';')])) for line in d['rows'].split('|')]
    v=d['variant']
    if v=='reorder':rows=[dict(reversed(list(r.items()))) for r in rows]
    if v=='missing_column':rows[0].pop('n_event')
    if v=='extra_column':rows[0]['extra']=1
    if v=='renamed_column':rows[0]['other']=rows[0].pop('n_event')
    if v=='wrong_container':return {'rows':rows}
    if v=='row_container':rows[0]=list(rows[0].values())
    if v=='classed_count':rows[0]['b']=decimal.Decimal('90')
    if v=='list_count':rows[0]['b']=[90]
    if v=='hostile_id':rows[0]['pair_id']=HostileString('SYN_A')
    return rows
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--work-dir',required=True);ap.add_argument('--rscript',required=True);a=ap.parse_args()
    output=Path(a.output).resolve();work=Path(a.work_dir).resolve()
    if output.exists() or not output.parent.is_dir() or ROOT==output or ROOT in output.parents or output in ROOT.parents:raise ValueError('New external output required')
    if not work.is_dir() or ROOT==work or ROOT in work.parents or work in ROOT.parents or os.name=='nt' and ' ' in str(work):raise ValueError('External no-space R work directory required')
    output.mkdir();guard=output/'guard cwd with spaces';guard.mkdir()
    code=(ROOT/'python/m1_validator.py').read_text();tree=ast.parse(code)
    assert all(isinstance(n,(ast.Import,ast.FunctionDef,ast.Expr)) for n in tree.body)
    assert {al.name for n in tree.body if isinstance(n,ast.Import) for al in n.names}=={'math','re'}
    forbidden={'open','read_csv','readRDS','connect','write','system','popen','Popen','eval','exec'}
    assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in forbidden for n in ast.walk(tree))
    # Execute module definitions with runtime IO and network creation blocked.
    original_open=builtins.open;original_socket=socket.socket
    def blocked(*args,**kwargs):raise AssertionError('Off-target IO attempted')
    oldcwd=Path.cwd();os.chdir(guard)
    try:
        builtins.open=blocked;socket.socket=blocked
        namespace={'__name__':'m1_import_audit'};exec(compile(code,'m1_validator.py','exec'),namespace)
    finally:builtins.open=original_open;socket.socket=original_socket;os.chdir(oldcwd)
    assert not list(guard.iterdir());validate=namespace['validate_sufficient_statistics']
    cases=read(ROOT/'fixtures/m1_cases.csv')+read(ROOT/'fixtures/m1_addendum_cases.csv');results=[]
    for d in cases:
        x=build(d);original=copy.deepcopy(x)
        try:answer=validate(x);status='ACCEPT';error=''
        except ValueError as e:answer=None;status='REJECT';error=str(e)
        passed=status==d['expected_status'] and error==d['expected_error']
        if answer:passed=passed and str(answer['N'])==d['expected_N'] and str(answer['row_count'])==d['expected_rows']
        # A stable representation handles NaNs while still detecting normal mutation.
        assert repr(x)==repr(original)
        results.append(dict(case_id=d['case_id'],status=status,error=error,passed=passed,N=str(answer['N']) if answer else '',row_count=str(answer['row_count']) if answer else '',pair_ids='~'.join(answer['pair_ids']) if answer else '',margins='~'.join(str(int(r['a'])+int(r['b']))+':'+str(int(r['a'])+int(r['c'])) for r in x) if answer else ''))
    write(output/'python_cases.csv',results);assert all(x['passed'] for x in results)
    base=dict(pair_id='SYN_NATIVE',a=10,b=90,c=20,d=880,n_drug=100,n_event=30)
    class OddInt(int):
        def __int__(self):raise AssertionError('Must not coerce hostile subclass')
    class OddFloat(float):pass
    class OddList(list):pass
    class OddDict(dict):pass
    mutations={
      'int_subclass':lambda:[dict(base,b=OddInt(90))],
      'float_subclass':lambda:[dict(base,b=OddFloat(90))],
      'decimal':lambda:[dict(base,b=decimal.Decimal('90'))],
      'complex':lambda:[dict(base,b=90+0j)],
      'bytes_count':lambda:[dict(base,b=b'90')],
      'tuple_count':lambda:[dict(base,b=(90,))],
      'dict_count':lambda:[dict(base,b={'n':90})],
      'list_subclass':lambda:OddList([base]),
      'dict_subclass':lambda:[OddDict(base)],
      'tuple_container':lambda:(base,),
      'generator_container':lambda:(r for r in [base]),
      'object_container':lambda:object(),
      'id_bytes':lambda:[dict(base,pair_id=b'SYN_NATIVE')],
      'id_subclass':lambda:[dict(base,pair_id=HostileString('SYN_NATIVE'))],
      'huge_arbitrary_precision':lambda:[dict(base,b=10**1000)]}
    native=[]
    for label,fn in mutations.items():
        try:validate(fn());passed=False
        except ValueError:passed=True
        native.append(dict(case_id=label,passed=passed))
    write(output/'python_native.csv',native);assert all(x['passed'] for x in native)
    env=os.environ.copy();env.update(LC_ALL='C',LANG='C',TZ='UTC',TEMP=str(work),TMP=str(work),TMPDIR=str(work),PYTHONDONTWRITEBYTECODE='1')
    cmd=[a.rscript,'--vanilla',str(ROOT/'tests/run_m1.R'),str(ROOT),str(output)]
    begin=time.monotonic();r=subprocess.run(cmd,cwd=guard,env=env,capture_output=True,text=True,timeout=90)
    (output/'r_execution.log').write_text(r.stdout+r.stderr,encoding='utf-8');(output/'r_command.json').write_text(json.dumps(dict(command=cmd,exit=r.returncode,seconds=time.monotonic()-begin),indent=2));assert r.returncode==0,r.stderr
    rrows={x['case_id']:x for x in read(output/'r_cases.csv')};assert len(rrows)==len(results)
    parity=[]
    for x in results:
        y=rrows[x['case_id']]
        for k in ['status','error']+(['N','row_count','pair_ids','margins'] if x['status']=='ACCEPT' else []):parity.append(dict(case_id=x['case_id'],check=k,passed=x[k]==y[k]))
    write(output/'parity_checks.csv',parity);assert all(x['passed'] for x in parity)
    assert not list(guard.iterdir())
    summary=dict(scope='SYNTHETIC_M1_ENGINEERING_ONLY',shared_cases=len(cases),python_native=len(native),r_native=len(read(output/'r_native.csv')),classification_and_error_checks=2*len(cases),accepted_exact_output_checks=sum(x['status']=='ACCEPT' for x in results)*4,parity_checks=len(parity),failures=0,python_import_io_blocked=True,r_import_binding_only=True,guard_directory_unchanged=True,python_version=sys.version.split()[0])
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
