"""Integration tests use actual functions; no scientific input or expected result table."""
from pathlib import Path
import argparse,copy,csv,hashlib,importlib.util,json,os,subprocess,sys,tempfile,unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--work-dir',required=True);ap.add_argument('--rscript',required=True);a=ap.parse_args();output=Path(a.output).resolve();work=Path(a.work_dir).resolve()
    if output.exists() or not output.parent.is_dir() or output==ROOT or ROOT in output.parents or output in ROOT.parents:raise ValueError('New external output required')
    output.mkdir();guard=output/'guard cwd with spaces';guard.mkdir();qc=load('integration_qc',ROOT/'tools/release_qc.py');m1=load('integration_m1',ROOT/'python/m1_validator.py');base=dict(pair_id='SYN_INTEGRATION',a=10,b=90,c=20,d=880,n_drug=100,n_event=30)
    class Tests(unittest.TestCase):
        def test_functions_coexist(self):self.assertTrue(callable(qc.metrics) and callable(m1.validate_sufficient_statistics))
        def test_shared_valid_count(self):self.assertEqual(m1.validate_sufficient_statistics([base])['N'],qc.metrics(10,90,20,880)['N'])
        def test_zero_a_contract_difference(self):
            self.assertEqual(qc.metrics(0,90,20,880)['state'],'UNDEFINED')
            with self.assertRaises(ValueError):m1.validate_sufficient_statistics([dict(base,a=0,n_drug=90,n_event=20)])
        def test_zero_b_structural_acceptance(self):
            self.assertTrue(m1.validate_sufficient_statistics([dict(base,a=1,b=0,c=4,d=995,n_drug=1,n_event=5)])['accepted']);self.assertEqual(qc.metrics(1,0,4,995)['state'],'UNDEFINED')
        def test_margin_failure_does_not_change_metrics(self):
            original=qc.metrics(10,90,20,880)
            with self.assertRaises(ValueError):m1.validate_sufficient_statistics([dict(base,n_drug=101)])
            self.assertEqual(qc.metrics(10,90,20,880),original)
        def test_duplicate_pair_contract(self):
            with self.assertRaises(ValueError):m1.validate_sufficient_statistics([base,base])
        def test_both_reject_boolean(self):
            with self.assertRaises(ValueError):qc.metrics(True,1,1,1)
            with self.assertRaises(ValueError):m1.validate_sufficient_statistics([dict(base,a=True)])
        def test_boundary_preserves_identifiers(self):
            L=2**53-1;x=dict(pair_id='0009007199254740993',a=L,b=0,c=0,d=0,n_drug=L,n_event=L);self.assertEqual(m1.validate_sufficient_statistics([x])['pair_ids'],[x['pair_id']]);self.assertEqual(qc.metrics(L,0,0,0)['N'],L)
        def test_functions_do_not_mutate(self):
            x=copy.deepcopy(base);m1.validate_sufficient_statistics([x]);qc.metrics(x['a'],x['b'],x['c'],x['d']);self.assertEqual(x,base);self.assertEqual(list(guard.iterdir()),[])
        def test_demo_repeat_and_spaces(self):
            hashes=[]
            for label in ['demo A with spaces','demo B with spaces']:
                dest=output/label;r=subprocess.run([sys.executable,'-I',str(ROOT/'run_m1_demo.py'),'--output',str(dest),'--work-dir',str(work),'--rscript',a.rscript],cwd=guard,capture_output=True,text=True,timeout=90);self.assertEqual(r.returncode,0,r.stderr);hashes.append({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir()})
            self.assertEqual(hashes[0],hashes[1]);self.assertEqual(len(hashes[0]),2);(output/'demo_repeat_hashes.json').write_text(json.dumps(hashes,sort_keys=True,indent=2))
        def test_missing_runtime_clean_failure(self):
            dest=output/'missing_runtime';r=subprocess.run([sys.executable,'-I',str(ROOT/'run_m1_demo.py'),'--output',str(dest),'--work-dir',str(work),'--rscript','missing_synthetic_r_command'],capture_output=True,text=True,timeout=30);self.assertNotEqual(r.returncode,0);self.assertFalse(dest.exists())
        def test_existing_output_preserved(self):
            dest=output/'existing';dest.mkdir();sentinel=dest/'sentinel.txt';sentinel.write_text('SYNTHETIC');r=subprocess.run([sys.executable,'-I',str(ROOT/'run_m1_demo.py'),'--output',str(dest),'--work-dir',str(work),'--rscript',a.rscript],capture_output=True,text=True,timeout=30);self.assertNotEqual(r.returncode,0);self.assertEqual(sentinel.read_text(),'SYNTHETIC')
        def test_combined_missing_runtime(self):
            dest=output/'combined_missing_runtime';r=subprocess.run([sys.executable,'-I',str(ROOT/'tools/run_all.py'),'--output',str(dest),'--work-dir',str(work),'--rscript','missing_synthetic_r_command'],capture_output=True,text=True,timeout=30);self.assertNotEqual(r.returncode,0);self.assertFalse(dest.exists())
        def test_combined_source_output_rejected(self):
            dest=ROOT/'UNAPPROVED_OUTPUT';r=subprocess.run([sys.executable,'-I',str(ROOT/'tools/run_all.py'),'--output',str(dest),'--work-dir',str(work),'--rscript',a.rscript],capture_output=True,text=True,timeout=30);self.assertNotEqual(r.returncode,0);self.assertFalse(dest.exists())
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));assert result.wasSuccessful()
    env=os.environ.copy();env.update(LC_ALL='C',LANG='C',TZ='UTC',TEMP=str(work),TMP=str(work),TMPDIR=str(work));r=subprocess.run([a.rscript,'--vanilla',str(ROOT/'tests/run_integration.R'),str(ROOT),str(output/'r_coexistence.csv')],cwd=guard,env=env,capture_output=True,text=True,timeout=60);(output/'r_coexistence.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
    with (output/'r_coexistence.csv').open() as f:rc=list(csv.DictReader(f))
    assert len(rc)==8 and all(x['passed']=='TRUE' for x in rc)
    summary=dict(python_integration_tests=result.testsRun,r_coexistence_checks=len(rc),demo_repeat_hash_checks=2,demo_exact_checks_per_execution=12,failures=0,scope='SYNTHETIC LOCAL INTEGRATION ONLY');(output/'SUMMARY.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n');print(json.dumps(summary,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
