"""Generic synthetic-count QC and release-file allowlist. No clinical analysis pipeline."""
from pathlib import Path
import csv,hashlib,math,re
ALLOWED={'.md','.py','.R','.csv','.json','.cff','.txt'}
def metrics(a,b,c,d):
    v=(a,b,c,d)
    if any(type(x) not in (int,float) or x<0 or x>2**53-1 or not math.isfinite(x) or x!=int(x) for x in v):raise ValueError('invalid counts')
    if sum(int(x) for x in v)>2**53-1:raise ValueError('table total exceeds exact integer range')
    result={'N':a+b+c+d,'ROR':None,'PRR':None,'LCL':None,'UCL':None,'state':'UNDEFINED'}
    if min(v)<=0:return result
    odds=(a*d)/(b*c);se=math.sqrt(sum(1/x for x in v));result.update(ROR=odds,PRR=(a/(a+b))/(c/(c+d)),LCL=math.exp(math.log(odds)-1.96*se),UCL=math.exp(math.log(odds)+1.96*se),state='DEFINED');return result
def secure_relative(value):
    p=Path(value)
    if value.startswith(('/',chr(92))) or p.is_absolute() or re.match(r'^[A-Za-z]:',value) or '..' in p.parts or '\\' in value:raise ValueError('unsafe relative path')
    return p
def scan(root):
    root=Path(root).resolve();findings=[]
    personal=re.compile(r'(?i)([A-Z]:[\\/]Users[\\/]|/(?:home|Users)/)')
    credential=re.compile(r'(?i)(?:password|api[_-]?key|client_secret|access_token)\s*[:=]\s*[\"\'][^\"\'\r\n]{8,}')
    for p in sorted(root.rglob('*')):
        if p.is_symlink():findings.append((str(p.relative_to(root)),'SYMLINK'));continue
        if not p.is_file():continue
        rel=p.relative_to(root).as_posix();secure_relative(rel)
        if p.suffix not in ALLOWED and p.name!='LICENSE' and rel!='.github/workflows/synthetic-qc.yml':findings.append((rel,'DISALLOWED_TYPE'));continue
        if p.stat().st_size>2097152:findings.append((rel,'SIZE_LIMIT'));continue
        try:t=p.read_text(encoding='utf-8-sig')
        except UnicodeError:findings.append((rel,'ENCODING'));continue
        if personal.search(t):findings.append((rel,'PERSONAL_PATH'))
        if credential.search(t):findings.append((rel,'CREDENTIAL_PATTERN_REQUIRES_REVIEW'))
    return findings
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_manifest(root,manifest):
    root=Path(root).resolve()
    with open(manifest,encoding='utf-8-sig',newline='') as f:rr=list(csv.DictReader(f))
    seen=set()
    for r in rr:
        rel=secure_relative(r['path']);name=rel.as_posix()
        if name in seen:raise ValueError('duplicate manifest key')
        seen.add(name);p=root/rel
        if p.is_symlink() or not p.is_file() or p.resolve().parent!=root and root not in p.resolve().parents:raise ValueError('missing or escaped manifest file')
        if digest(p)!=r['sha256'] or p.stat().st_size!=int(r['bytes']):raise ValueError('manifest mismatch')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.resolve()!=Path(manifest).resolve()}
    if actual!=seen:raise ValueError('extra or missing file')
    return len(rr)
