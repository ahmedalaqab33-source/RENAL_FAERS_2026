from pathlib import Path
import argparse,subprocess,sys,json
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--work-dir',required=True);p.add_argument('--rscript',required=True);a=p.parse_args();out=Path(a.output);out.mkdir()
 result=subprocess.run([sys.executable,'-I',str(ROOT/'modules/m2/test_m2.py'),'--output',str(out/'suite')],check=False)
 if result.returncode:return result.returncode
 summary=json.loads((out/'suite/SUMMARY.json').read_text());assert summary['tests_run']==31 and summary['failures']==summary['errors']==summary['skipped']==0
 (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
