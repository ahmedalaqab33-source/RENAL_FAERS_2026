"""Executable synthetic M2 correctness, failure and conservation tests."""
from pathlib import Path
import sys,os,json,csv,hashlib,random,tempfile,copy,subprocess,unittest,collections
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from m2_engine import audit,AuditError,digest,SCHEMAS
from m2_generate import generate,write_package,parent

def modern(rid='SYN_R1',cid='SYN_C1',ver='1',year=2018):return dict(era='modern',kind='demo',year=year,quarter=1,report_id=rid,case_id=cid,case_version=ver)
def child(rid='SYN_R1',era='modern',year=2018):return dict(era=era,kind='drug',year=year,quarter=1,parent_id=rid,drug_seq='1',role='PS')
def rich():
 a=modern();return [a,dict(a),modern(cid='SYN_C2'),modern(rid='SYN_R2'),modern(year=2019),modern('合成_0003','SYN_C3'),dict(era='legacy',kind='demo',year=2011,quarter=1,isr='SYN_R1',case='SYN_LEG_C',i_f_cod='F',foll_seq='02'),child(),child('SYN_R2'),child('SYN_R1','legacy',2011),child('SYN_MISSING')]
def oracle(rows):
 # Bounded test-only in-memory grouping, independent of SQL and engine validation.
 demo=[r for r in rows if r['kind']=='demo'];drugs=[r for r in rows if r['kind']=='drug'];reps=collections.defaultdict(list);tuples=collections.defaultdict(list);cases=collections.defaultdict(set);phys=set();contexts=collections.defaultdict(set)
 for r in rows:phys.add(json.dumps(r,sort_keys=True,ensure_ascii=False,separators=(',',':')))
 for r in demo:
  rid=r['report_id'] if r['era']=='modern' else r['isr'];cid=r['case_id'] if r['era']=='modern' else r['case'];reps[(r['era'],rid)].append(r)
  if cid is not None and cid!='':cases[(r['era'],cid)].add(r['year'])
  if r['era']=='modern':tuples[(cid,r['case_version'])].append(rid)
  contexts[(r['era'],rid)].add(json.dumps({k:v for k,v in r.items() if k not in ['year','quarter']},sort_keys=True,ensure_ascii=False))
 conflicts=0
 for (era,rid),rs in reps.items():
  if era=='modern' and (len({r['case_id'] for r in rs})>1 or len({r['case_version'] for r in rs})>1):conflicts+=1
 parent_classes=collections.Counter(len(contexts[(r['era'],r['parent_id'])]) for r in drugs)
 return dict(stored_rows=len(rows),demo_rows=len(demo),drug_rows=len(drugs),distinct_physical_fingerprints=len(phys),report_namespace_groups=len(reps),stored_case_namespace_groups=len(cases),modern_tuple_groups=len(tuples),modern_tuple_extra_occurrences=sum(len(x)-1 for x in tuples.values()),modern_tuple_multiple_reports=sum(len(set(x))>1 for x in tuples.values()),modern_report_conflicts=conflicts,report_cross_year_groups=sum(len({r['year'] for r in rs})>1 for rs in reps.values()),case_cross_year_groups=sum(len(y)>1 for y in cases.values()),legacy_missing_case_rows=sum(r['era']=='legacy' and r['case'] in (None,'') for r in demo),modern_literal_concat_matches=sum(r['era']=='modern' and r['report_id']==r['case_id']+r['case_version'] for r in demo),modern_literal_concat_mismatches=sum(r['era']=='modern' and r['report_id']!=r['case_id']+r['case_version'] for r in demo),exact_physical_duplicate_excess=len(rows)-len(phys),orphan_child_rows=parent_classes[0],unambiguous_child_rows=parent_classes[1],ambiguous_child_rows=sum(n for k,n in parent_classes.items() if k>1))

class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='m2_synthetic_',dir=OUTPUT);self.root=Path(self.tmp.name);self.work=self.root/'work';self.work.mkdir();self.counter=0
 def tearDown(self):self.tmp.cleanup()
 def run_rows(self,rows,batch=3,**kw):
  self.counter+=1;src=self.root/('input'+str(self.counter));write_package(src,rows);dest=self.root/('out'+str(self.counter));answer,tel=audit(src,dest,self.work,batch_size=batch,**kw);return answer,dest,tel,src
 def test_schema_registry_matches_implementation(self):self.assertEqual(json.loads((ROOT/'schema_registry.json').read_text())['schemas'],SCHEMAS)
 def test_independent_global_oracle(self):
  rows=rich();ans,dest,_,_=self.run_rows(rows);self.assertEqual(ans['metrics'],oracle(rows));self.assertEqual(ans['status'],'QC_FINDINGS');self.assertFalse((dest/'_SUCCESS').exists());self.assertEqual(ans['metrics']['orphan_child_rows'],1);self.assertEqual(ans['metrics']['ambiguous_child_rows'],1)
 def test_chunk_size_invariance(self):
  results=[self.run_rows(rich(),b)[0] for b in [1,2,4,64]];self.assertTrue(all(x['metrics']==results[0]['metrics'] and x['multiset_sha256']==results[0]['multiset_sha256'] for x in results))
 def test_order_invariance_global_not_source_lineage(self):
  rows=rich();a=self.run_rows(rows)[0];random.Random(77).shuffle(rows);b=self.run_rows(rows)[0];self.assertEqual(a['metrics'],b['metrics']);self.assertEqual(a['multiset_sha256'],b['multiset_sha256']);self.assertNotEqual(a['source_sha256'],b['source_sha256'])
 def test_exact_conservation_and_disjoint_chunks(self):
  rows=rich();ans,dest,_,_=self.run_rows(rows,2);chunks=[json.loads(x) for x in (dest/'chunks.jsonl').read_text().splitlines()];self.assertEqual(sum(x['physical_rows'] for x in chunks),len(rows));self.assertEqual(ans['inserted_rows'],ans['valid_rows_seen']);self.assertEqual(ans['physical_rows_seen'],ans['valid_rows_seen']+ans['quarantined_rows']);self.assertTrue(all(a['last_ordinal']+1==b['first_ordinal'] for a,b in zip(chunks,chunks[1:])));CONSERVATION.append({k:ans[k] for k in ['physical_rows_seen','valid_rows_seen','quarantined_rows','inserted_rows']})
 def test_deterministic_products_same_source_batch(self):
  a,pa,_,_=self.run_rows(rich(),2);b,pb,_,_=self.run_rows(rich(),2);self.assertEqual({f.name:digest(f) for f in pa.iterdir()},{f.name:digest(f) for f in pb.iterdir()})
 def test_namespace_isolation(self):
  rows=[modern('SYN_COLLISION'),dict(era='legacy',kind='demo',year=2011,quarter=1,isr='SYN_COLLISION',case='SYN_OTHER',i_f_cod='I',foll_seq=''),child('SYN_COLLISION'),child('SYN_COLLISION','legacy',2011)];a=self.run_rows(rows)[0];self.assertEqual(a['metrics']['report_namespace_groups'],2);self.assertEqual(a['metrics']['unambiguous_child_rows'],2)
 def test_exact_duplicate_not_contradictory(self):
  a=self.run_rows([modern(),modern(),child()])[0];self.assertEqual(a['metrics']['exact_physical_duplicate_excess'],1);self.assertEqual(a['metrics']['modern_report_conflicts'],0);self.assertEqual(a['metrics']['unambiguous_child_rows'],1)
 def test_global_conflicts_across_chunk_boundaries(self):
  a=self.run_rows([modern(),child(),modern(cid='SYN_OTHER')],1)[0];self.assertEqual(a['metrics']['modern_report_conflicts'],1);self.assertEqual(a['metrics']['ambiguous_child_rows'],1)
 def test_cross_year_diagnostics_not_patients(self):
  a=self.run_rows([modern(),modern(year=2019)])[0];self.assertEqual(a['metrics']['report_cross_year_groups'],1);self.assertEqual(a['metrics']['case_cross_year_groups'],1);self.assertEqual(a['metrics']['modern_tuple_extra_occurrences'],1)
 def test_opaque_unicode_long_leading_zero_ids(self):
  ids=['0001','1','é','e\u0301','合成'+('长'*298)];rows=[modern(x,'SYN_CASE_'+str(i)) for i,x in enumerate(ids)];a,dest,_,_=self.run_rows(rows);self.assertEqual(a['metrics']['report_namespace_groups'],5);self.assertEqual(a['status'],'CLEAN');public=(dest/'audit.json').read_text();self.assertNotIn('合成',public);self.assertNotIn('SYN_CASE_',public)
 def test_legacy_follow_sequence_not_modern_version(self):
  rows=[dict(era='legacy',kind='demo',year=2010,quarter=1,isr='SYN_LEG',case=None,i_f_cod='F',foll_seq='001-UNKNOWN')];a=self.run_rows(rows)[0];self.assertEqual(a['metrics']['modern_tuple_groups'],0);self.assertEqual(a['metrics']['legacy_missing_case_rows'],1)
 def test_transition_quarter_schema_distinction(self):
  r=modern();r.update(year=2012,quarter=4);self.assertEqual(self.run_rows([r])[0]['status'],'CLEAN');r['quarter']=3;self.assertEqual(self.run_rows([r])[0]['status'],'INPUT_REJECTED')
 def test_adversarial_schema_value_quarantine(self):
  mutations={'null_id':dict(report_id=None),'blank_id':dict(report_id=''),'whitespace':dict(report_id=' SYN_R1'),'numeric_id':dict(report_id=9007199254740993),'float_id':dict(report_id=1.0),'bool_id':dict(report_id=True),'version_leadingzero':dict(case_version='01'),'version_floatstring':dict(case_version='1.5'),'version_numeric':dict(case_version=1),'version_negative':dict(case_version='-1'),'version_huge':dict(case_version='2147483648'),'long_id':dict(report_id='X'*513),'control_id':dict(report_id='SYN\x00'),'extra_column':dict(extra='synthetic'),'bool_year':dict(year=True),'float_year':dict(year=2018.0),'bad_role':None,'missing_column':None,'kind':dict(kind='unknown')}
  for label,change in mutations.items():
   with self.subTest(case=label):
    row=modern()
    if label=='bad_role':row=child();row['role']='UNRECOGNIZED'
    elif label=='missing_column':row.pop('case_id')
    else:row.update(change)
    a,d,_,_=self.run_rows([row]);self.assertEqual(a['status'],'INPUT_REJECTED');self.assertEqual(a['quarantined_rows'],1);self.assertEqual(a['physical_rows_seen'],1);self.assertFalse((d/'_SUCCESS').exists());ADVERSARIAL.append(label)
 def test_invalid_json_duplicate_keys_blank_utf8(self):
  for label,raw in [('json',b'{not-json}\n'),('duplicate',b'{"era":"modern","era":"legacy"}\n'),('blank',b'\n'),('utf8',b'\xff\n'),('nan',b'{"n":NaN}\n')]:
   with self.subTest(case=label):
    self.counter+=1;src=self.root/('raw'+str(self.counter));write_package(src,[modern()]);(src/'records.jsonl').write_bytes(raw);meta=json.loads((src/'manifest.json').read_text());meta.update(bytes=len(raw),sha256=digest(src/'records.jsonl'));(src/'manifest.json').write_text(json.dumps(meta));dest=self.root/('rawout'+str(self.counter));a,_=audit(src,dest,self.work);self.assertEqual(a['status'],'INPUT_REJECTED');self.assertFalse((dest/'_SUCCESS').exists())
 def test_injected_failure_has_no_success_and_accounts_pending(self):
  a,d,_,_=self.run_rows([modern(str(i),'SYN_'+str(i)) for i in range(10)],2,fail_after=3);self.assertEqual(a['status'],'PROCESSING_FAILED');self.assertFalse(a['complete']);self.assertEqual(a['physical_rows_seen'],3);self.assertEqual(a['pending_uninserted_rows'],1);self.assertFalse((d/'_SUCCESS').exists());self.assertFalse(list(self.work.iterdir()))
 def test_manifest_tamper_rejected_before_processing(self):
  src=self.root/'tampered';write_package(src,[modern()]);(src/'records.jsonl').write_text('{}\n');dest=self.root/'noout'
  with self.assertRaises(AuditError):audit(src,dest,self.work)
  self.assertFalse(dest.exists())
 def test_source_and_work_preservation(self):
  src=self.root/'preserved';write_package(src,rich());before={f.name:(digest(f),f.stat().st_mtime_ns) for f in src.iterdir()};a,_=audit(src,self.root/'preservedout',self.work,1);self.assertEqual(before,{f.name:(digest(f),f.stat().st_mtime_ns) for f in src.iterdir()});self.assertFalse(list(self.work.iterdir()))
 def test_no_identifier_leak_in_aggregate_products(self):
  a,d,_,_=self.run_rows([modern('SYN_PRIVATE_SENTINEL','SYN_CASE_SECRET'),child('SYN_PRIVATE_SENTINEL')]);self.assertNotIn('SYN_PRIVATE_SENTINEL',''.join(f.read_text() for f in d.iterdir()));self.assertNotIn('SYN_CASE_SECRET',''.join(f.read_text() for f in d.iterdir()))
 def test_output_no_clobber(self):
  src=self.root/'clobber';write_package(src,[modern()]);dest=self.root/'existing';dest.mkdir();(dest/'sentinel').write_text('SYNTHETIC')
  with self.assertRaises(AuditError):audit(src,dest,self.work)
  self.assertEqual((dest/'sentinel').read_text(),'SYNTHETIC')
 def test_unsafe_output_inside_source(self):
  src=self.root/'unsafe';write_package(src,[modern()])
  with self.assertRaises(AuditError):audit(src,src/'out',self.work)
 def test_invalid_resource_contracts(self):
  src=self.root/'resources';write_package(src,[modern()])
  for b in [0,-1,True,4097,1.5]:
   with self.assertRaises(AuditError):audit(src,self.root/'out',self.work,batch_size=b)
 def test_manifest_unapproved_extra_file(self):
  src=self.root/'extras';write_package(src,[modern()]);(src/'extra.txt').write_text('SYNTHETIC')
  with self.assertRaises(AuditError):audit(src,self.root/'out',self.work)
 def test_line_size_fails_closed(self):
  src=self.root/'longline';write_package(src,[modern()]);raw=b'X'*17000+b'\n';(src/'records.jsonl').write_bytes(raw);m=json.loads((src/'manifest.json').read_text());m.update(bytes=len(raw),sha256=digest(src/'records.jsonl'));(src/'manifest.json').write_text(json.dumps(m));a,_=audit(src,self.root/'longout',self.work);self.assertEqual(a['status'],'PROCESSING_FAILED');self.assertFalse(a['complete'])
 def test_manifest_count_mismatch_fails_closed(self):
  src=self.root/'count';write_package(src,[modern()]);m=json.loads((src/'manifest.json').read_text());m['records']=2;(src/'manifest.json').write_text(json.dumps(m));a,_=audit(src,self.root/'countout',self.work);self.assertEqual(a['status'],'PROCESSING_FAILED');self.assertFalse((self.root/'countout/_SUCCESS').exists())
 def test_generator_repeatability_and_clean_audit(self):
  a=self.root/'gen1';b=self.root/'gen2';generate(a,200,19);generate(b,200,19);self.assertEqual(digest(a/'records.jsonl'),digest(b/'records.jsonl'));ans,_=audit(a,self.root/'genout',self.work,batch_size=17);self.assertEqual(ans['status'],'CLEAN');self.assertEqual(ans['physical_rows_seen'],200)
 def test_schema_drift_receipt_no_raw_identifier(self):
  a,d,_,_=self.run_rows([dict(modern(),unapproved='SYN_IDENT_SECRET')]);receipt=(d/'quarantine.jsonl').read_text();self.assertNotIn('SYN_IDENT_SECRET',receipt);self.assertIn('SCHEMA_DRIFT',receipt)
 def test_atomic_manifest_and_success_gate(self):
  a,d,_,_=self.run_rows([modern()]);self.assertTrue((d/'_SUCCESS').exists());m=json.loads((d/'OUTPUT_MANIFEST.json').read_text());self.assertTrue(all(digest(d/k)==v['sha256'] for k,v in m.items()));self.assertFalse(list(self.root.glob('.m2-stage-*')));self.assertFalse(list(self.root.glob('*.lock')))
 def test_timeout_fails_closed(self):
  a,d,_,_=self.run_rows([modern()],timeout=1e-12);self.assertEqual(a['status'],'PROCESSING_FAILED');self.assertFalse(a['complete']);self.assertFalse((d/'_SUCCESS').exists())
 def test_cooperative_lock_is_not_overwritten(self):
  src=self.root/'lockedinput';write_package(src,[modern()]);dest=self.root/'lockedout';lock=self.root/'lockedout.lock';lock.write_text('SYNTHETIC_OTHER_WRITER')
  with self.assertRaises(FileExistsError):audit(src,dest,self.work)
  self.assertEqual(lock.read_text(),'SYNTHETIC_OTHER_WRITER');self.assertFalse(dest.exists())
 def test_bound_statement_hostile_string_stays_data(self):
  rid="SYN'); DROP TABLE records; --";a,d,_,_=self.run_rows([modern(rid),child(rid)]);self.assertEqual(a['status'],'CLEAN');self.assertEqual(a['metrics']['stored_rows'],2);self.assertNotIn(rid,(d/'audit.json').read_text())

OUTPUT=None;CONSERVATION=[];ADVERSARIAL=[]
def main():
 import argparse
 global OUTPUT
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);x=parser.parse_args();OUTPUT=Path(x.output).resolve()
 if OUTPUT.exists():raise ValueError('New external test directory required')
 OUTPUT.mkdir();r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));summary=dict(tests_run=r.testsRun,failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped),adversarial_schema_subcases=len(ADVERSARIAL),scope='Entirely synthetic local M2 tests')
 (OUTPUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2));(OUTPUT/'ADVERSARIAL_SUBCASES.json').write_text(json.dumps(ADVERSARIAL,indent=2))
 if CONSERVATION:
  with (OUTPUT/'CONSERVATION.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(CONSERVATION[0]));w.writeheader();w.writerows(CONSERVATION)
 print(json.dumps(summary));return 0 if r.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
