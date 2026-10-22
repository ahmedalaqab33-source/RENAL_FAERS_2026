from pathlib import Path
import sys,importlib.util,csv,unittest,tempfile,json
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('release_qc',root/'tools/release_qc.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
class Tests(unittest.TestCase):
 def test_known_counts(self):self.assertAlmostEqual(q.metrics(10,90,20,880)['ROR'],44/9)
 def test_prr(self):self.assertAlmostEqual(q.metrics(10,90,20,880)['PRR'],4.5)
 def test_zero_unknown(self):self.assertIsNone(q.metrics(1,0,4,995)['ROR'])
 def test_negative(self):
  with self.assertRaises(ValueError):q.metrics(-1,2,3,4)
 def test_fractional(self):
  with self.assertRaises(ValueError):q.metrics(1.2,2,3,4)
 def test_not_finite(self):
  with self.assertRaises(ValueError):q.metrics(float('nan'),2,3,4)
 def test_traversal(self):
  with self.assertRaises(ValueError):q.secure_relative('../escape')
 def test_absolute(self):
  with self.assertRaises(ValueError):q.secure_relative('/absolute')
 def test_drive(self):
  with self.assertRaises(ValueError):q.secure_relative('X:/absolute')
 def test_manifest_tamper(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'one.txt').write_text('original');m=p/'manifest.csv'
   with m.open('w',newline='') as f:w=csv.writer(f);w.writerow(['path','sha256','bytes']);w.writerow(['one.txt',q.digest(p/'one.txt'),8])
   self.assertEqual(q.verify_manifest(p,m),1);(p/'one.txt').write_text('changed')
   with self.assertRaises(ValueError):q.verify_manifest(p,m)
 def test_manifest_extra(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'one.txt').write_text('one');m=p/'manifest.csv'
   with m.open('w',newline='') as f:w=csv.writer(f);w.writerow(['path','sha256','bytes']);w.writerow(['one.txt',q.digest(p/'one.txt'),3])
   (p/'extra.txt').write_text('extra')
   with self.assertRaises(ValueError):q.verify_manifest(p,m)
 def test_scan_negative_fixture(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'unsafe.txt').write_text('api'+'_key = '+chr(39)+'SYNTHETIC_NOT_A_REAL_SECRET'+chr(39));self.assertTrue(q.scan(p))
 def test_unapproved_binary(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'forbidden.rds').write_bytes(b'fixture');self.assertTrue(q.scan(p))
if __name__=='__main__':unittest.main()
