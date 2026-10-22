"""Bounded local dispatcher for existing QC and authentic M1 synthetic contracts."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,shutil,subprocess,sys,time,signal
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def external(p):return p!=ROOT and ROOT not in p.parents and p not in ROOT.parents
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--work-dir',required=True);ap.add_argument('--rscript',default='Rscript');a=ap.parse_args()
    try:
        output=Path(a.output).resolve();work=Path(a.work_dir).resolve();r=shutil.which(a.rscript)
        if not external(output) or output.exists() or not output.parent.is_dir():raise ValueError('New external output required')
        if not external(work) or not work.is_dir() or os.name=='nt' and ' ' in str(work) or not r:raise ValueError('Work directory/runtime unavailable')
        spec=importlib.util.spec_from_file_location('all_qc',ROOT/'tools/release_qc.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q);q.verify_manifest(ROOT,ROOT/'RELEASE_MANIFEST.csv')
        if q.scan(ROOT) or shutil.disk_usage(work).free<268435456:raise ValueError('Security/disk preflight')
        before={p.relative_to(ROOT).as_posix():q.digest(p) for p in ROOT.rglob('*') if p.is_file()};output.mkdir();(output/'logs').mkdir();cwd=output/'unrelated cwd with spaces';cwd.mkdir();commands=[];start=time.monotonic()
        for name,script in [('count_qc','tools/run_ci.py'),('m1','tests/run_m1.py'),('integration','tests/run_integration.py'),('m2','tests/run_m2_suite.py'),('cross_module','tests/run_cross_module.py')]:
            if time.monotonic()-start>900 or shutil.disk_usage(work).free<268435456:raise ValueError('Total budget/disk reserve')
            cmd=[sys.executable,'-I',str(ROOT/script),'--output',str(output/name),'--work-dir',str(work),'--rscript',r];begin=time.monotonic();kw={'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP} if os.name=='nt' else {'start_new_session':True}
            proc=subprocess.Popen(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,**kw)
            try:text,_=proc.communicate(timeout=min(300,max(1,900-(time.monotonic()-start))))
            except subprocess.TimeoutExpired:
                if os.name=='nt':subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
                else:os.killpg(proc.pid,signal.SIGKILL)
                proc.communicate();raise ValueError('Integrated command timeout')
            (output/'logs'/(name+'.log')).write_text(text,encoding='utf-8');commands.append(dict(label=name,command=cmd,exit=proc.returncode,seconds=time.monotonic()-begin));(output/'executed_commands.json').write_text(json.dumps(commands,indent=2))
            if proc.returncode:raise ValueError('Integrated suite failed: '+name)
        after={p.relative_to(ROOT).as_posix():q.digest(p) for p in ROOT.rglob('*') if p.is_file()}
        if before!=after:raise ValueError('Source changed')
        summary=dict(scope='SYNTHETIC ENGINEERING ONLY; PRIVATE INTEGRATION; NO HOSTED ATTESTATION',failures=0,source_preserved=True,count_qc=json.loads((output/'count_qc/CI_SUMMARY.json').read_text()),m1=json.loads((output/'m1/SUMMARY.json').read_text()),integration=json.loads((output/'integration/SUMMARY.json').read_text()),m2=json.loads((output/'m2/SUMMARY.json').read_text()),cross_module=json.loads((output/'cross_module/SUMMARY.json').read_text()))
        (output/'INTEGRATED_SUMMARY.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n');print(json.dumps(summary,sort_keys=True));return 0
    except (ValueError,OSError) as e:print('INTEGRATED_QC_ERROR: '+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
