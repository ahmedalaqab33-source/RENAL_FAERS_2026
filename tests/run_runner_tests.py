"""Synthetic runner contract tests; all mutations are in disposable component copies."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,subprocess,sys,tempfile,unittest
sys.dont_write_bytecode=True
SOURCE=Path(__file__).resolve().parents[1]
RSCRIPT=None
class Runner(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='synthetic_runner_')
        self.base=Path(self.temp.name);self.component=self.base/'component with spaces'
        shutil.copytree(SOURCE,self.component);self.cwd=self.base/'unrelated working directory';self.cwd.mkdir()
        self.work=self.base/'temporary_work';self.work.mkdir()
    def tearDown(self):self.temp.cleanup()
    def invoke(self,*extra,output=None,rscript=None,code=0):
        out=Path(output) if output is not None else self.base/'new output'
        command=[sys.executable,'-I',str(self.component/'run_demo.py'),'--output',str(out),'--rscript',rscript or RSCRIPT,'--work-dir',str(self.work)]+list(extra)
        result=subprocess.run(command,cwd=self.cwd,capture_output=True,text=True,timeout=90)
        self.assertEqual(result.returncode,code,result.stderr)
        if code!=0:self.assertFalse((out/'summary.json').exists())
        return out
    def change(self,edit,rebind=True):
        f=self.component/'fixtures/demo_counts.csv'
        with f.open(newline='',encoding='utf-8') as h:rows=list(csv.reader(h))
        edit(rows)
        with f.open('w',newline='',encoding='utf-8') as h:csv.writer(h,lineterminator='\n').writerows(rows)
        if rebind:self.rebind(f)
    def rebind(self,f):
        manifest=self.component/'RELEASE_MANIFEST.csv'
        with manifest.open(encoding='utf-8',newline='') as h:rows=list(csv.DictReader(h))
        for row in rows:
            if row['path']==f.relative_to(self.component).as_posix():row['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();row['bytes']=str(f.stat().st_size)
        with manifest.open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fieldnames=['path','sha256','bytes']);w.writeheader();w.writerows(rows)
    def bad_cell(self,value):
        self.change(lambda rows:rows[1].__setitem__(1,value));self.invoke(code=2)
    def test_demo_and_parity(self):
        out=self.invoke();summary=json.loads((out/'summary.json').read_text())
        self.assertEqual(summary['rows'],4);self.assertEqual(summary['undefined_rows'],2);self.assertEqual(summary['numeric_parity_checks'],20)
        self.assertEqual(set(x.name for x in out.iterdir()),{'synthetic_results.csv','summary.json','OUTPUT_MANIFEST.csv'})
        with (out/'OUTPUT_MANIFEST.csv').open(newline='') as h:
            for row in csv.DictReader(h):self.assertEqual(hashlib.sha256((out/row['path']).read_bytes()).hexdigest(),row['sha256'])
    def test_repeated_output_bytes(self):
        a=self.invoke(output=self.base/'run one');b=self.invoke(output=self.base/'run two')
        self.assertEqual({x.name:x.read_bytes() for x in a.iterdir()},{x.name:x.read_bytes() for x in b.iterdir()})
    def test_original_fixture(self):
        out=self.invoke('--fixture','synthetic_counts.csv');summary=json.loads((out/'summary.json').read_text());self.assertEqual(summary['rows'],3);self.assertEqual(summary['numeric_parity_checks'],15)
    def test_root_working_directory(self):
        self.cwd=self.component;self.invoke()
    def test_traversal_fixture(self):self.invoke('--fixture','../external.csv',code=2)
    def test_external_fixture(self):self.invoke('--fixture',str(self.base/'anything.csv'),code=2)
    def test_missing_r(self):self.invoke(rscript='missing_synthetic_r_executable',code=2)
    def test_wrong_interpreter(self):self.invoke(rscript=sys.executable,code=3)
    def test_bad_header(self):self.change(lambda x:x[0].__setitem__(1,'unexpected'));self.invoke(code=2)
    def test_fractional(self):self.bad_cell('1.25')
    def test_negative(self):self.bad_cell('-1')
    def test_boolean_true(self):self.bad_cell('TRUE')
    def test_boolean_false(self):self.bad_cell('FALSE')
    def test_blank_missing(self):self.bad_cell('')
    def test_null_missing(self):self.bad_cell('null')
    def test_typed_missing_token(self):self.bad_cell('NA')
    def test_nonfinite(self):self.bad_cell('NaN')
    def test_above_limit(self):self.bad_cell('9007199254740992')
    def test_table_total_limit(self):
        self.change(lambda x:x.__setitem__(1,['SYNTHETIC_TOTAL_LIMIT','9007199254740991','1','0','0']));self.invoke(code=2)
    def test_exact_maximum(self):
        self.change(lambda x:x.__setitem__(1,['SYNTHETIC_MAXIMUM','9007199254740991','0','0','0']));out=self.invoke()
        with (out/'synthetic_results.csv').open(newline='') as h:row=next(csv.DictReader(h))
        self.assertEqual(row['N'],'9007199254740991');self.assertEqual(row['state'],'UNDEFINED')
    def test_bad_label(self):self.change(lambda x:x[1].__setitem__(0,'BAD_LABEL'));self.invoke(code=2)
    def test_duplicate_label(self):self.change(lambda x:x[2].__setitem__(0,x[1][0]));self.invoke(code=2)
    def test_extra_column(self):self.change(lambda x:x[1].append('extra'));self.invoke(code=2)
    def test_missing_column(self):self.change(lambda x:x[1].pop());self.invoke(code=2)
    def test_row_limit(self):
        self.change(lambda x:x.__setitem__(slice(1,None),[['SYNTHETIC_ROW_'+str(i),'1','2','3','4'] for i in range(33)]));self.invoke(code=2)
    def test_empty_fixture(self):self.change(lambda x:x.__delitem__(slice(1,None)));self.invoke(code=2)
    def test_leading_zero(self):self.bad_cell('01')
    def test_hash_mismatch(self):self.change(lambda x:x[1].__setitem__(1,'11'),rebind=False);self.invoke(code=2)
    def test_unlisted_component_file(self):
        (self.component/'unexpected.txt').write_text('synthetic extra file');self.invoke(code=2)
    def test_output_inside_component(self):
        out=self.component/'output';self.invoke(output=out,code=2);self.assertFalse(out.exists())
    def test_output_parent_is_component_ancestor(self):self.invoke(output=self.base,code=2)
    def test_existing_output_preserved(self):
        out=self.base/'existing output';out.mkdir();(out/'marker.txt').write_text('SYNTHETIC_KEEP')
        self.invoke(output=out,code=2);self.assertEqual((out/'marker.txt').read_text(),'SYNTHETIC_KEEP')
    def test_missing_output_parent(self):self.invoke(output=self.base/'absent parent'/'out',code=2)
    def test_work_directory_inside_component(self):self.invoke('--work-dir',str(self.component),code=2)
    def test_missing_work_directory(self):self.invoke('--work-dir',str(self.base/'absent_work'),code=2)
    def test_invalid_utf8(self):
        f=self.component/'fixtures/demo_counts.csv';f.write_bytes(b'\xff\xfe');self.rebind(f);self.invoke(code=2)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--rscript',required=True);args=parser.parse_args();RSCRIPT=args.rscript
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Runner))
    raise SystemExit(not result.wasSuccessful())
