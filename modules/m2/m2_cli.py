"""Synthetic-only M2 command line; never an original FAERS loader."""
from pathlib import Path
import argparse,json,sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m2_engine import audit,AuditError
from m2_generate import generate
def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 g=sub.add_parser('generate');g.add_argument('--output',required=True);g.add_argument('--rows',type=int,default=2000);g.add_argument('--seed',type=int,default=42)
 a=sub.add_parser('audit');a.add_argument('--input',required=True);a.add_argument('--output',required=True);a.add_argument('--work-dir',required=True);a.add_argument('--batch-size',type=int,default=256);a.add_argument('--timeout',type=int,default=60);a.add_argument('--inject-failure-after',type=int)
 x=p.parse_args()
 try:
  if x.command=='generate':print(json.dumps(generate(x.output,x.rows,x.seed),sort_keys=True));return 0
  result,telemetry=audit(x.input,x.output,x.work_dir,x.batch_size,x.timeout,x.inject_failure_after);print(json.dumps(dict(status=result['status'],telemetry=telemetry),sort_keys=True));return {'CLEAN':0,'QC_FINDINGS':3,'INPUT_REJECTED':2,'PROCESSING_FAILED':2}[result['status']]
 except (AuditError,ValueError,OSError) as e:print(json.dumps(dict(status='BLOCKED',error=type(e).__name__)),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
