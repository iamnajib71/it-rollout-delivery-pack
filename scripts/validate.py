"""Fail closed on broken provenance, mismatched story coverage and invalid demo."""
from pathlib import Path
import csv, hashlib, json, re, sys
CORE = '--core' in sys.argv
ROOT=Path(__file__).resolve().parents[1]
def require(condition, message):
    if not condition: raise AssertionError(message)
def rows(path):
    with (ROOT/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
    manifest=json.loads((ROOT/'evidence/manifest.json').read_text())
    require(len(manifest['source_commit'])==40,'Source revision missing')
    for item in manifest['files']:
        p=ROOT/item['path'];require(p.is_file(),f'Missing {p}')
        require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Evidence changed: {p}')
    print(f"PASS provenance: {len(manifest['files'])} exact source snapshots")
    backlog=rows('backlog.csv');rtm=rows('business-analysis/traceability.csv');uat=rows('testing/uat-cases.csv')
    require(list(backlog[0])==['Summary','Issue Type','Description','Acceptance Criteria','Priority','Epic Link','Story Points'],'Jira headers incorrect')
    require(len(backlog)==len(rtm)==len(uat)==25,'Expected 25 records in each mapping')
    ids=[r['Summary'].split(':')[0] for r in backlog]
    require(set(ids)=={f'US-{n:02d}' for n in range(1,26)},'Story ID uniqueness / range')
    require(set(ids)=={r['Story ID'] for r in rtm}=={r['Story ID'] for r in uat},'Missing traceability')
    for story in backlog:
        require(story['Issue Type']=='Story','Invalid issue type')
        require(story['Priority'] in ['High','Medium'],'Invalid priority')
        require(story['Story Points'].isdigit(),'Non-numeric estimate')
        require(not story['Epic Link'],'Invented Jira epic key')
        require(re.match(r'^Given .+\nWhen .+\nThen .+\.$',story['Acceptance Criteria']), 'GWT missing')
    case_by_story={r['Story ID']:r for r in uat}
    for row in rtm:
        text=(ROOT/row['Evidence file']).read_text(encoding='utf-8-sig')
        require(row['Exact proof'] in text,f"Unsupported story {row['Story ID']}")
        case=case_by_story[row['Story ID']]
        require(case['UAT ID']==row['UAT ID'] and case['Evidence file']==row['Evidence file'] and case['Exact proof']==row['Exact proof'],'RTM/UAT mismatch')
        require(case['Run timestamp'].startswith('2026-10-06'),'Invented historical date')
        require(case['Limit'] and row['Limit'],'Evidence scope absent')
        for source in row['Homelab test / case'].split(' / '):require((ROOT/'evidence/homelab'/source).exists(),f'Missing runner/case {source}')
    print('PASS traceability: 25 stories, 25 UAT mappings, every exact proof found')
    for path in sorted(ROOT.glob('*/*.md')):
        if path.parent.name in ['initiation','business-analysis','planning','control','testing','closure']:
            require('fictional' in path.read_text().lower(),f'Fictional label absent: {path}')
    for row in rows('initiation/raci.csv'):
        require(sum('A' in v for k,v in row.items() if k!='Activity')==1,'RACI accountability conflict')
    for row in rows('planning/budget.csv'):
        require(float(row['Quantity'])*float(row['Unit AUD ex GST'])==float(row['Total AUD ex GST']),'Budget arithmetic error')
    require(len(rows('control/raid.csv'))>=10,'RAID incomplete')
    require({r['Type'] for r in rows('control/raid.csv')}=={'Risk','Assumption','Issue','Dependency'},'RAID types missing')
    for section in ['initiation','business-analysis','planning','control','testing','closure','scripts']:
        require((ROOT/section).is_dir(),f'Missing section {section}')
    for path in [ROOT/'README.md', *ROOT.glob('*/*.md')]:
        if path.parent.name=='evidence':continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
            if target.startswith(('http:','https:','#')):continue
            if CORE and target.endswith(('demo.gif','IT-Rollout-Delivery-Pack.pdf')):continue
            require((path.parent/target.split('#')[0]).exists(),f'Broken link: {path.name} -> {target}')
    print('PASS artefacts: labels, RACI, budget arithmetic, RAID and local links')
    if CORE:
        print('RESULT: 0 failed core checks (historical homelab results unchanged)')
        return
    from PIL import Image
    with Image.open(ROOT/'docs/demo.gif') as im:
        duration=0
        for n in range(im.n_frames):im.seek(n);duration+=im.info.get('duration',0)
        require(30000<=duration<=90000,f'Demo duration {duration}ms out of range')
    cast=[json.loads(x) for x in (ROOT/'docs/demo.cast').read_text().splitlines()]
    require(cast[0]['version']==2 and cast[-1][0]>=30,'Recording invalid')
    with Image.open(ROOT/'docs/social-preview.png') as im:require(im.size==(1280,640),'Social preview dimensions')
    from pypdf import PdfReader
    pdf=PdfReader(ROOT/'pack/IT-Rollout-Delivery-Pack.pdf')
    text='\n'.join(p.extract_text() for p in pdf.pages)
    for term in ['Project charter','Business requirements','CR-001','US-25','Rollback','Historical lab']:
        require(term.lower() in text.lower(),f'PDF missing section {term}')
    print(f'PASS media: {duration/1000:.1f}s GIF, 1280x640 preview, {len(pdf.pages)}-page PDF')
    print('RESULT: 0 failed pack checks (historical homelab results unchanged)')
if __name__=='__main__':
    try:main()
    except Exception as e:print(f'FAIL: {e}',file=sys.stderr);sys.exit(1)
