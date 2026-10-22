from pathlib import Path
import sys,importlib.util,json
sys.dont_write_bytecode=True
root=Path(sys.argv[1]).resolve();s=importlib.util.spec_from_file_location('release_qc',Path(__file__).with_name('release_qc.py'));q=importlib.util.module_from_spec(s);s.loader.exec_module(q);findings=q.scan(root)
if findings:raise SystemExit('Candidate screening failed; review locally')
n=q.verify_manifest(root,root/'RELEASE_MANIFEST.csv');print(json.dumps({'verified_files':n,'status':'VERIFIED PASS','scope':'Bytes and bounded patterns only; release rights remain HOLD'}))
