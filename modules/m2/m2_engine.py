"""Bounded synthetic namespace/lineage auditor; no real FAERS or reference access."""
import hashlib,json,os,re,sqlite3,tempfile,time,unicodedata,shutil
from pathlib import Path

SCHEMAS={
 'legacy_demo':['era','kind','year','quarter','isr','case','i_f_cod','foll_seq'],
 'modern_demo':['era','kind','year','quarter','report_id','case_id','case_version'],
 'legacy_drug':['era','kind','year','quarter','parent_id','drug_seq','role'],
 'modern_drug':['era','kind','year','quarter','parent_id','drug_seq','role']}
LIMITS={'input_bytes':33554432,'line_bytes':16384,'records':100000,'id_characters':512,'id_utf8_bytes':4096,'batch':4096,'sqlite_bytes':268435456}
class AuditError(ValueError):pass
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(65536),b''):h.update(block)
 return h.hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')
def no_duplicates(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise AuditError('DUPLICATE_JSON_KEY')
  d[k]=v
 return d
def load_json(raw):return json.loads(raw,object_pairs_hook=no_duplicates,parse_constant=lambda value:(_ for _ in ()).throw(AuditError('NONFINITE_JSON')))
def opaque(value,optional=False):
 if optional and value is None:return None
 if type(value) is not str:raise AuditError('ID_TYPE')
 if optional and value=='':return value
 if not value or value!=value.strip() or len(value)>512 or len(value.encode('utf-8'))>4096 or any(unicodedata.category(c).startswith('C') for c in value):raise AuditError('ID_SYNTAX')
 return value
def positive(value):
 if type(value) is not str or re.fullmatch(r'[1-9][0-9]{0,9}',value,flags=re.ASCII) is None or int(value)>2147483647:raise AuditError('VERSION_OR_SEQUENCE')
 return value
def validate(row):
 if type(row) is not dict:raise AuditError('ROW_CONTAINER')
 era=row.get('era');kind=row.get('kind')
 if type(era) is not str or type(kind) is not str or era+'_'+kind not in SCHEMAS:raise AuditError('SCHEMA_VERSION_OR_KIND')
 if set(row)!=set(SCHEMAS[era+'_'+kind]):raise AuditError('SCHEMA_DRIFT')
 year=row['year'];quarter=row['quarter']
 if type(year) is not int or type(quarter) is not int or not 2004<=year<=2025 or not 1<=quarter<=4:raise AuditError('YEAR_QUARTER')
 modern=year>=2013 or year==2012 and quarter==4
 if (era=='modern')!=modern:raise AuditError('ERA_SCHEMA')
 if kind=='demo':
  if era=='modern':rid=opaque(row['report_id']);cid=opaque(row['case_id']);version=positive(row['case_version'])
  else:
   rid=opaque(row['isr']);cid=opaque(row['case'],True);version=None;opaque(row['i_f_cod'],True);opaque(row['foll_seq'],True)
  seq=role=None
 else:
  rid=opaque(row['parent_id']);cid=version=None;seq=positive(row['drug_seq']);role=row['role']
  if type(role) is not str or role not in ['PS','SS','C','I']:raise AuditError('ROLE')
 physical=hashlib.sha256(canonical(row)).hexdigest()
 context=hashlib.sha256(canonical({k:v for k,v in row.items() if k not in ['year','quarter']})).hexdigest()
 return era,kind,year,quarter,rid,cid,version,seq,role,physical,context
def write_json(path,data):
 with open(path,'w',encoding='utf-8',newline='\n') as f:json.dump(data,f,sort_keys=True,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
def package(input_dir):
 root=Path(input_dir)
 if root.is_symlink() or getattr(root,'is_junction',lambda:False)():raise AuditError('INPUT_LINK')
 root=root.resolve()
 if {p.name for p in root.iterdir()}!={'manifest.json','records.jsonl'}:raise AuditError('INPUT_MEMBERSHIP')
 for p in root.iterdir():
  if p.is_symlink() or not p.is_file():raise AuditError('INPUT_LINK_OR_TYPE')
 manifest=root/'manifest.json';data=root/'records.jsonl'
 if manifest.stat().st_size>16384 or data.stat().st_size>LIMITS['input_bytes']:raise AuditError('INPUT_SIZE')
 m=load_json(manifest.read_bytes())
 if type(m) is not dict or set(m)!={'schema_version','synthetic','generator','seed','records','bytes','sha256'}:raise AuditError('MANIFEST_SCHEMA')
 if m['schema_version']!='M2_SYNTHETIC_V1' or m['synthetic'] is not True or m['generator']!='m2_generator_v1':raise AuditError('SYNTHETIC_CONTRACT')
 if type(m['seed']) is not int or type(m['records']) is not int or not 1<=m['records']<=LIMITS['records'] or type(m['bytes']) is not int:raise AuditError('MANIFEST_COUNTS')
 if m['bytes']!=data.stat().st_size or m['sha256']!=digest(data):raise AuditError('SOURCE_HASH')
 return root,data,manifest,m
def global_metrics(c):
 scalar=lambda sql:int(c.execute(sql).fetchone()[0] or 0)
 result={
 'stored_rows':scalar('SELECT count(*) FROM records'),
 'demo_rows':scalar("SELECT count(*) FROM records WHERE kind='demo'"),
 'drug_rows':scalar("SELECT count(*) FROM records WHERE kind='drug'"),
 'distinct_physical_fingerprints':scalar('SELECT count(DISTINCT physical) FROM records'),
 'report_namespace_groups':scalar("SELECT count(*) FROM (SELECT era,rid FROM records WHERE kind='demo' GROUP BY era,rid)"),
 'stored_case_namespace_groups':scalar("SELECT count(*) FROM (SELECT era,cid FROM records WHERE kind='demo' AND cid IS NOT NULL AND cid<>'' GROUP BY era,cid)"),
 'modern_tuple_groups':scalar("SELECT count(*) FROM (SELECT cid,ver FROM records WHERE era='modern' AND kind='demo' GROUP BY cid,ver)"),
 'modern_tuple_extra_occurrences':scalar("SELECT coalesce(sum(n-1),0) FROM (SELECT count(*) n FROM records WHERE era='modern' AND kind='demo' GROUP BY cid,ver)"),
 'modern_tuple_multiple_reports':scalar("SELECT count(*) FROM (SELECT cid,ver FROM records WHERE era='modern' AND kind='demo' GROUP BY cid,ver HAVING count(DISTINCT rid)>1)"),
 'modern_report_conflicts':scalar("SELECT count(*) FROM (SELECT rid FROM records WHERE era='modern' AND kind='demo' GROUP BY rid HAVING count(DISTINCT cid)>1 OR count(DISTINCT ver)>1)"),
 'report_cross_year_groups':scalar("SELECT count(*) FROM (SELECT era,rid FROM records WHERE kind='demo' GROUP BY era,rid HAVING count(DISTINCT year)>1)"),
 'case_cross_year_groups':scalar("SELECT count(*) FROM (SELECT era,cid FROM records WHERE kind='demo' AND cid IS NOT NULL AND cid<>'' GROUP BY era,cid HAVING count(DISTINCT year)>1)"),
 'legacy_missing_case_rows':scalar("SELECT count(*) FROM records WHERE kind='demo' AND era='legacy' AND (cid IS NULL OR cid='')"),
 'modern_literal_concat_matches':scalar("SELECT count(*) FROM records WHERE kind='demo' AND era='modern' AND rid=cid||ver"),
 'modern_literal_concat_mismatches':scalar("SELECT count(*) FROM records WHERE kind='demo' AND era='modern' AND rid<>cid||ver")}
 result['exact_physical_duplicate_excess']=result['stored_rows']-result['distinct_physical_fingerprints']
 c.execute("CREATE TEMP TABLE parent_contexts AS SELECT era,rid,count(DISTINCT context) n FROM records WHERE kind='demo' GROUP BY era,rid")
 c.execute('CREATE INDEX parent_key ON parent_contexts(era,rid)')
 for name,clause in [('orphan_child_rows','p.n IS NULL'),('unambiguous_child_rows','p.n=1'),('ambiguous_child_rows','p.n>1')]:result[name]=scalar("SELECT count(*) FROM records r LEFT JOIN parent_contexts p ON r.era=p.era AND r.rid=p.rid WHERE r.kind='drug' AND "+clause)
 assert result['demo_rows']+result['drug_rows']==result['stored_rows']
 assert result['orphan_child_rows']+result['unambiguous_child_rows']+result['ambiguous_child_rows']==result['drug_rows']
 return result
def audit(input_dir,output_dir,work_dir,batch_size=256,timeout=60,fail_after=None):
 if type(batch_size) is not int or not 1<=batch_size<=4096 or type(timeout) not in [int,float] or not 0<timeout<=300:raise AuditError('RESOURCE_CONFIG')
 if fail_after is not None and (type(fail_after) is not int or fail_after<1):raise AuditError('FAILURE_INJECTION_CONFIG')
 root,data,manifest,meta=package(input_dir);output=Path(output_dir).resolve();work=Path(work_dir).resolve();code_root=Path(__file__).resolve().parent
 for protected in [root,code_root]:
  if output==protected or protected in output.parents or output in protected.parents or work==protected or protected in work.parents or work in protected.parents:raise AuditError('OUTPUT_WORK_SCOPE')
 if output.exists() or not output.parent.is_dir() or not work.is_dir():raise AuditError('OUTPUT_EXISTS_OR_PARENT')
 if shutil.disk_usage(work).free<1073741824:raise AuditError('DISK_FLOOR')
 lock=output.with_name(output.name+'.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
 stage=Path(tempfile.mkdtemp(prefix='.m2-stage-',dir=output.parent));(stage/'chunks.jsonl').touch();start=time.monotonic();seen=valid=rejected=inserted=0;complete=False;reason=None;metrics={};error_counts={};temp_peak=0;context_digest=None
 original=(data.stat().st_size,data.stat().st_mtime_ns,manifest.stat().st_size,manifest.stat().st_mtime_ns,digest(manifest))
 try:
  with tempfile.TemporaryDirectory(prefix='m2-work-',dir=work) as tmp:
   tmp=Path(tmp);db=tmp/'synthetic.sqlite';c=sqlite3.connect(db)
   def progress():return int(time.monotonic()-start>timeout)
   c.set_progress_handler(progress,1000);c.execute('PRAGMA page_size=4096');c.execute('PRAGMA cache_size=-8192');c.execute('PRAGMA temp_store=MEMORY');c.execute('PRAGMA hard_heap_limit=67108864');c.execute('PRAGMA max_page_count=65536');c.execute('PRAGMA journal_mode=DELETE')
   c.execute('CREATE TABLE records (ordinal INTEGER PRIMARY KEY,era TEXT,kind TEXT,year INTEGER,quarter INTEGER,rid TEXT,cid TEXT,ver TEXT,seq TEXT,role TEXT,physical TEXT,context TEXT)')
   c.execute('CREATE INDEX keyed ON records(era,kind,rid)');c.execute('CREATE INDEX case_versions ON records(era,kind,cid,ver)')
   def disk():return sum(p.stat().st_size for p in tmp.rglob('*') if p.is_file())
   pending=[];chunk_hash=hashlib.sha256();first=1;chunk_valid=chunk_bad=0
   def flush():
    nonlocal inserted,temp_peak,first,chunk_valid,chunk_bad,chunk_hash
    if pending:
     with c:c.executemany('INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',pending)
     inserted+=len(pending);pending.clear()
    temp_peak=max(temp_peak,disk())
    if temp_peak>LIMITS['sqlite_bytes'] or shutil.disk_usage(work).free<1073741824:raise AuditError('TEMP_DISK_CAP')
    if first<=seen:
     ch=dict(first_ordinal=first,last_ordinal=seen,physical_rows=seen-first+1,accepted_rows=chunk_valid,quarantined_rows=chunk_bad,raw_bytes_sha256=chunk_hash.hexdigest());assert ch['physical_rows']==chunk_valid+chunk_bad
     with open(stage/'chunks.jsonl','a',encoding='utf-8',newline='\n') as cf:cf.write(json.dumps(ch,sort_keys=True)+'\n')
    first=seen+1;chunk_valid=chunk_bad=0;chunk_hash=hashlib.sha256()
   try:
    with open(data,'rb') as f,open(stage/'quarantine.jsonl','w',encoding='utf-8',newline='\n') as quarantine:
     while True:
      if time.monotonic()-start>timeout:raise AuditError('TIMEOUT')
      raw=f.readline(LIMITS['line_bytes']+1)
      if not raw:break
      if len(raw)>LIMITS['line_bytes']:raise AuditError('LINE_SIZE_FATAL')
      seen+=1
      if seen>LIMITS['records']:raise AuditError('RECORD_LIMIT')
      chunk_hash.update(raw)
      try:
       row=load_json(raw.decode('utf-8'));values=validate(row)
      except (AuditError,ValueError,UnicodeError,TypeError) as exc:
       code=str(exc) if isinstance(exc,AuditError) else 'UTF8_OR_JSON_PARSE' if isinstance(exc,(UnicodeError,ValueError)) else 'ROW_TYPE';error_counts[code]=error_counts.get(code,0)+1
       rejected+=1;chunk_bad+=1;quarantine.write(json.dumps(dict(ordinal=seen,error=code,raw_sha256=hashlib.sha256(raw).hexdigest()),sort_keys=True)+'\n')
      else:valid+=1;chunk_valid+=1;pending.append((seen,)+values)
      if seen%batch_size==0:flush()
      if fail_after is not None and seen>=fail_after:raise AuditError('INJECTED_FAILURE')
     flush();complete=True
    if seen!=meta['records']:raise AuditError('MANIFEST_ROW_COUNT')
    if digest(data)!=meta['sha256'] or original!=(data.stat().st_size,data.stat().st_mtime_ns,manifest.stat().st_size,manifest.stat().st_mtime_ns,digest(manifest)):raise AuditError('SOURCE_CHANGED')
    assert valid+rejected==seen and inserted==valid
    metrics=global_metrics(c);temp_peak=max(temp_peak,disk())
    if temp_peak>LIMITS['sqlite_bytes']:raise AuditError('TEMP_DISK_CAP')
    h=hashlib.sha256()
    for fingerprint,count in c.execute('SELECT physical,count(*) FROM records GROUP BY physical ORDER BY physical'):h.update((fingerprint+':'+str(count)+'\n').encode('ascii'))
    context_digest=h.hexdigest()
   except (AuditError,sqlite3.Error,AssertionError,OSError,MemoryError) as e:
    reason=e.args[0] if isinstance(e,AuditError) else type(e).__name__;complete=False
   finally:c.close()
  findings=any(metrics.get(k,0)>0 for k in ['modern_tuple_multiple_reports','modern_report_conflicts','orphan_child_rows','ambiguous_child_rows'])
  status='PROCESSING_FAILED' if reason else 'INPUT_REJECTED' if rejected else 'QC_FINDINGS' if findings else 'CLEAN'
  summary=dict(schema_version='M2_SYNTHETIC_V1',status=status,complete=complete,error=reason,error_counts=error_counts,expected_records=meta['records'],physical_rows_seen=seen,valid_rows_seen=valid,quarantined_rows=rejected,inserted_rows=inserted,pending_uninserted_rows=valid-inserted,metrics=metrics,multiset_sha256=context_digest,source_sha256=meta['sha256'],input_manifest_sha256=original[-1],batch_size=batch_size,interpretation='Synthetic stored-record diagnostics only; no patients,eligibility,case selection or chemical identity inference')
  write_json(stage/'audit.json',summary)
  if status=='CLEAN':(stage/'_SUCCESS').write_text('SYNTHETIC_AUDIT_CLEAN\n',encoding='ascii')
  products={f.name:dict(sha256=digest(f),bytes=f.stat().st_size) for f in sorted(stage.iterdir()) if f.is_file()};write_json(stage/'OUTPUT_MANIFEST.json',products)
  if output.exists():raise AuditError('OUTPUT_RACE')
  os.rename(stage,output)
  return summary,dict(wall_seconds=time.monotonic()-start,temp_disk_max_observed_bytes=temp_peak,sqlite_page_cap_bytes=LIMITS['sqlite_bytes'],cache_target_bytes=8388608)
 finally:
  if stage.exists():shutil.rmtree(stage)
  lock.unlink(missing_ok=True)
