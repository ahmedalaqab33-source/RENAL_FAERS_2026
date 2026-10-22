"""Eight finite synthetic CI boundary tests; no complete test-suite recursion."""
from pathlib import Path
import csv,hashlib,importlib.util,shutil,subprocess,sys,tempfile,unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('q',ROOT/'tools/release_qc.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
bs=importlib.util.spec_from_file_location('bootstrap',ROOT/'tools/ci_bootstrap.py');b=importlib.util.module_from_spec(bs);bs.loader.exec_module(b)
class Guards(unittest.TestCase):
    def test_unapproved_yaml_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'arbitrary.yml').write_text('name: synthetic');self.assertTrue(q.scan(p))
    def test_only_named_workflow_allowed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'.github/workflows';p.mkdir(parents=True);(p/'synthetic-qc.yml').write_text('name: synthetic');self.assertFalse(q.scan(Path(t)))
    def test_checkout_metadata_excluded_without_git(self):
        with tempfile.TemporaryDirectory() as t:
            source=Path(t)/'source';shutil.copytree(ROOT,source);meta=source/'.git';meta.mkdir();(meta/'SYNTHETIC_METADATA_ONLY.txt').write_text('not a Git initialization')
            dest=Path(t)/'component';b.stage_component(source,dest);self.assertFalse((dest/'.git').exists())
            with (dest/'RELEASE_MANIFEST.csv').open() as h:expected=len(list(csv.DictReader(h)))
            self.assertEqual(q.verify_manifest(dest,dest/'RELEASE_MANIFEST.csv'),expected)
    def test_unlisted_checkout_content_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            source=Path(t)/'source';shutil.copytree(ROOT,source);(source/'unlisted.txt').write_text('SYNTHETIC')
            with self.assertRaises(ValueError):b.stage_component(source,Path(t)/'out')
    def test_manifest_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            source=Path(t)/'source';shutil.copytree(ROOT,source);(source/'fixtures/demo_counts.csv').write_text('SYNTHETIC_INVALID')
            with self.assertRaises(ValueError):b.stage_component(source,Path(t)/'out')
    def test_missing_runtime_not_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            result=subprocess.run([sys.executable,'-I',str(ROOT/'tools/run_ci.py'),'--output',str(Path(t)/'out'),'--work-dir',t,'--rscript','missing_synthetic_r_command'],capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertFalse((Path(t)/'out').exists())
    def test_invalid_time_budget_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            result=subprocess.run([sys.executable,'-I',str(ROOT/'tools/run_ci.py'),'--output',str(Path(t)/'out'),'--work-dir',t,'--command-timeout','0'],capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertFalse((Path(t)/'out').exists())
    def test_source_output_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            result=subprocess.run([sys.executable,'-I',str(ROOT/'tools/run_ci.py'),'--output',str(ROOT/'invalid_output'),'--work-dir',t],capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertFalse((ROOT/'invalid_output').exists())
if __name__=='__main__':unittest.main()
