"""Deterministic entirely artificial legacy/modern package generator."""
from pathlib import Path
import json,random,hashlib
def parent(index):
 i=index-1 if index>0 and index%97==0 else index
 if i%4==0:return dict(era='legacy',kind='demo',year=2010+i%2,quarter=1,isr='SYN_ISR_000'+str(i),case='SYN_LEG_CASE_'+str(i//4),i_f_cod='I' if i%8==0 else 'F',foll_seq='' if i%8==0 else '1')
 cid='SYN_CASE_000'+str(i//3);version=str(i%3+1)
 if i%101==1:cid='SYN_案例_é_'+str(i//3)
 return dict(era='modern',kind='demo',year=2013+i%13,quarter=1,report_id=cid+version,case_id=cid,case_version=version)
def rows(count,seed):
 rng=random.Random(seed);n=count//2
 for i in range(n):yield parent(i)
 for i in range(count-n):
  p=parent(rng.randrange(n));yield dict(era=p['era'],kind='drug',year=p['year'],quarter=p['quarter'],parent_id=p['isr'] if p['era']=='legacy' else p['report_id'],drug_seq=str(i+1),role=['PS','SS','C','I'][i%4])
def write_package(root,records,seed=42):
 root=Path(root);root.mkdir();h=hashlib.sha256();n=0
 with (root/'records.jsonl').open('wb') as f:
  for row in records:
   raw=(json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8');f.write(raw);h.update(raw);n+=1
 meta=dict(schema_version='M2_SYNTHETIC_V1',synthetic=True,generator='m2_generator_v1',seed=seed,records=n,bytes=(root/'records.jsonl').stat().st_size,sha256=h.hexdigest())
 (root/'manifest.json').write_text(json.dumps(meta,sort_keys=True,indent=2)+'\n',encoding='utf-8');return meta
def generate(root,count=2000,seed=42):
 if type(count) is not int or not 2<=count<=100000:raise ValueError('Synthetic size must be2..100000')
 return write_package(root,rows(count,seed),seed)
