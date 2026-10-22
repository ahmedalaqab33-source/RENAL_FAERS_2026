"""Cross-module engineering tests; entirely synthetic, no clinical inference."""
from pathlib import Path
import sys,argparse,json,importlib.util,hashlib,subprocess
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--work-dir',required=True);p.add_argument('--rscript',required=True);a=p.parse_args();o=Path(a.output);o.mkdir();w=Path(a.work_dir)
 sys.path.insert(0,str(ROOT/'modules/m2'));engine=load('m2_engine','modules/m2/m2_engine.py');gen=load('m2_generate','modules/m2/m2_generate.py');q=load('qc_cross','tools/release_qc.py');m=load('m1_cross','python/m1_validator.py');checks=[]
 def check(label,condition):
  if not condition:raise AssertionError(label)
  checks.append(label)
 before={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in ROOT.rglob('*') if f.is_file()}
 check('QC positive synthetic estimate',q.metrics(4,6,2,8)['state']=='DEFINED')
 check('QC zero remains undefined',q.metrics(0,6,2,8)['state']=='UNDEFINED')
 for fun in [lambda:q.metrics(True,2,3,4),lambda:m.validate_sufficient_statistics([dict(pair_id='SYN',a=True,b=2,c=3,d=4,n_drug=3,n_event=4)])]:
  try:fun()
  except ValueError:checks.append('Boolean rejected by independent module')
  else:raise AssertionError('Boolean accepted')
 row=dict(pair_id='SYN',a=4,b=6,c=2,d=8,n_drug=10,n_event=6);original=dict(row);m.validate_sufficient_statistics([row]);check('M1 validation does not mutate fixture',row==original)
 src=o/'synthetic input with spaces';gen.generate(src,200,1729);source_hash=engine.digest(src/'records.jsonl');results=[];dirs=[]
 for i,b in enumerate([1,64,64]):
  dest=o/('output with spaces '+str(i));r,t=engine.audit(src,dest,w,batch_size=b);results.append(r);dirs.append(dest)
 check('M2 clean conservation',all(r['status']=='CLEAN' and r['physical_rows_seen']==r['valid_rows_seen']+r['quarantined_rows']==200 and r['inserted_rows']==200 for r in results))
 check('M2 batch invariant metrics',all(r['metrics']==results[0]['metrics'] for r in results))
 check('M2 batch invariant multiset',len({r['multiset_sha256'] for r in results})==1)
 check('M2 deterministic output bytes',{f.name:engine.digest(f) for f in dirs[1].iterdir()}=={f.name:engine.digest(f) for f in dirs[2].iterdir()})
 check('M2 fixture preserved',engine.digest(src/'records.jsonl')==source_hash)
 cmd=[sys.executable,'-I',str(ROOT/'modules/m2/m2_cli.py'),'audit','--input',str(src),'--output',str(o/'cli output'),'--work-dir',str(w),'--batch-size','64']
 r=subprocess.run(cmd,cwd=o,stdout=subprocess.PIPE,stderr=subprocess.PIPE);check('Portable isolated CLI from unrelated cwd',r.returncode==0)
 check('CLI matches direct engine',json.loads((o/'cli output/audit.json').read_text())['metrics']==results[0]['metrics'])
 after={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in ROOT.rglob('*') if f.is_file()};check('Complete integrated source immutable',before==after)
 summary=dict(tests_run=len(checks),failures=0,checks=checks,scope='SYNTHETIC ENGINEERING ONLY');(o/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));return 0
if __name__=='__main__':raise SystemExit(main())
