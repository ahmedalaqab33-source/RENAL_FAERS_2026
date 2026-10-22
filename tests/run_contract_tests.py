"""Synthetic-only count-contract regression cases; no third-party dependencies."""
from pathlib import Path
import csv,importlib.util,sys,unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('staged_qc',ROOT/'tools/release_qc.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
class Classed(float): pass
class Named(float): pass
def decode(t):
    if t.startswith('n:'):return int(t[2:])
    if t.startswith('f:'):return float(t[2:])
    return {'bool_true':True,'bool_false':False,'negative':-1,'fractional':1.25,
      'nan':float('nan'),'posinf':float('inf'),'neginf':-float('inf'),
      'null':None,'missing_real':None,'missing_integer':None,'missing_logical':None,
      'char_number':'1','blank':'','vector':[1,2],'empty_vector':[], 'list':[1],
      'complex':complex(1,1),'classed':Classed(1),'named':Named(1),
      'above_limit':2**53}[t]
with (ROOT/'fixtures/contract_cases.csv').open(encoding='utf-8',newline='') as h:CASES=list(csv.DictReader(h))
RESULTS=[]
class Contract(unittest.TestCase):pass
def make_test(row):
    def test(self):
        inputs=[decode(row[k]) for k in ['a','b','c','d']]
        result=None
        try:result=q.metrics(*inputs);actual='ACCEPT'
        except ValueError:actual='REJECT'
        rec={'case_id':row['case_id'],'expected':row['expected'],'actual':actual}
        rec.update({k:(result[k] if result else None) for k in ['N','ROR','PRR','LCL','UCL']})
        RESULTS.append(rec);self.assertEqual(actual,row['expected'])
    return test
for row in CASES:setattr(Contract,'test_'+row['case_id'],make_test(row))
class PythonOnly(unittest.TestCase):
    def test_arbitrary_precision_out_of_range(self):
        with self.assertRaises(ValueError):q.metrics(10**1000,2,3,4)
if __name__=='__main__':
    output=Path(sys.argv[1]).resolve()
    if output==ROOT or ROOT in output.parents:raise SystemExit('Write diagnostics outside component')
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Contract),unittest.defaultTestLoader.loadTestsFromTestCase(PythonOnly)])
    outcome=unittest.TextTestRunner(verbosity=2).run(suite)
    with output.open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=['case_id','expected','actual','N','ROR','PRR','LCL','UCL']);w.writeheader();w.writerows(RESULTS)
    raise SystemExit(not outcome.wasSuccessful())
