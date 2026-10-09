"""Build the portable delivery pack from Markdown and CSV, no external programs."""
from pathlib import Path
import csv, re, html, textwrap
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'pack/IT-Rollout-Delivery-Pack.pdf'
SECTIONS = ['initiation', 'business-analysis', 'planning', 'control', 'testing', 'closure']
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body', fontName='Helvetica', fontSize=9, leading=12, spaceAfter=6, splitLongWords=True, allowWidows=False, allowOrphans=False))
styles.add(ParagraphStyle(name='CodeSmall', fontName='Courier', fontSize=7, leading=10, spaceAfter=0))
styles['Heading1'].textColor = colors.HexColor('#16324f')
styles['Heading2'].textColor = colors.HexColor('#216b82')
def inline(text):
    text = text.replace('\u2014', '-').replace('\u2013', '-').replace('\u2011', '-')
    text = re.sub(r'!\[([^]]*)\]\([^)]*\)', r'Image: \1 (see GitHub)', text)
    text = re.sub(r'\[([^]]*)\]\(([^)]*)\)', r'\1 (\2)', text)
    text = html.escape(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)
    return text
def para(text, style='Body'):
    return Paragraph(inline(text), styles[style])
def markdown(path):
    flow = []; lines = path.read_text(encoding='utf-8-sig').splitlines(); i=0
    while i < len(lines):
        line=lines[i]; i+=1
        if not line.strip(): continue
        if line.startswith('```'):
            language=line[3:]; block=[]
            while i<len(lines) and not lines[i].startswith('```'):
                block.append(lines[i]); i+=1
            i+=1
            code_flow=[para('Diagram source - renders on GitHub' if language=='mermaid' else language, 'Heading3')]
            for row in block:
                for wrapped in textwrap.wrap(row, width=94, replace_whitespace=False, drop_whitespace=False) or [' ']:
                    code_flow.append(Paragraph(html.escape(wrapped).replace(' ', '&#160;'), styles['CodeSmall']))
            code_flow.append(Spacer(1,8)); flow.append(KeepTogether(code_flow)); continue
        if line.startswith('|'):
            rows=[line]
            while i<len(lines) and lines[i].startswith('|'): rows.append(lines[i]); i+=1
            parsed=[[c.strip() for c in r.strip('|').split('|')] for r in rows]
            headers=parsed[0]; data=parsed[2:]
            # Wide log tables become readable records instead of tiny columns.
            is_raci=headers[1:]==['SP','PC','IT','FM','HR','UR','SO']
            if len(headers)>6 and not is_raci:
                for row in data:
                    record=[para(row[0], 'Heading3')]
                    for h,v in zip(headers[1:],row[1:]): record.append(para(f'**{h}:** {v}'))
                    flow.append(KeepTogether(record))
            else:
                cells=[[para(c) for c in r] for r in [headers]+data]
                widths=[170]+[(A4[0]-258)/7]*7 if is_raci else [(A4[0]-88)/len(headers)]*len(headers)
                t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
                t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0f5')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#d1dce5')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]))
                flow.append(t);flow.append(Spacer(1,8))
            continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#')); flow.append(para(line[level:].strip(), 'Heading1' if level==1 else 'Heading2' if level==2 else 'Heading3'))
        else: flow.append(para(line.lstrip('> ')))
    return flow
def csv_records(path):
    flow=[para(path.stem.replace('-', ' ').title(),'Heading1'),para(f'Source: {path.relative_to(ROOT).as_posix()}')]
    with path.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    if path.name=='raci.csv':
        headers=list(rows[0]);cells=[[para(h) for h in headers]]+[[para(r[h]) for h in headers] for r in rows]
        t=Table(cells,colWidths=[170]+[(A4[0]-258)/7]*7,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0f5')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#d1dce5'))]))
        return flow+[t]
    for row in rows:
        first=next(iter(row)); record=[para(f'{first}: {row[first]}','Heading3')]
        for key,val in list(row.items())[1:]:
            if val: record.append(para(f'**{key}:** {val}'.replace('\n',' / ')))
        flow.append(KeepTogether(record))
    return flow
def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#d1dce5'));canvas.line(44,38,A4[0]-44,38)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#526779'))
    canvas.drawString(44,25,'Nazmul Hassan | Fictional office / historical lab evidence')
    canvas.drawRightString(A4[0]-44,25,str(doc.page))
def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    flow=[Spacer(1,60),para('IT Rollout Delivery Pack','Title'),para('Project delivery and business analysis case study','Heading2'),Spacer(1,18),para('Nazmul Hassan | 9 October 2026'),para('Fictional 15-person Cedar Office. Technical proof comes from the IT Support Homelab, recorded 6 October 2026.'),para('Lab acceptance only. Real-office deployment is on hold pending security, staffed UAT, physical print and recovery evidence.'),Spacer(1,18),para('Reading order','Heading2')]
    for s in SECTIONS:flow.append(para(s.replace('-',' ').title()))
    flow.append(para('CSV records are expanded for legibility. Mermaid diagram source is preserved; GitHub displays the diagrams. Source links and evidence hashes are in the repository.'))
    flow.append(PageBreak());flow+=markdown(ROOT/'README.md')
    for section in SECTIONS:
        for path in sorted((ROOT/section).glob('*')):
            if path.suffix not in ['.md','.csv']:continue
            flow.append(PageBreak());flow.append(para('Source: '+path.relative_to(ROOT).as_posix()))
            flow += markdown(path) if path.suffix=='.md' else csv_records(path)
    flow.append(PageBreak());flow+=csv_records(ROOT/'backlog.csv')
    flow.append(PageBreak());flow.append(para('Evidence provenance','Heading1'))
    import json
    m=json.loads((ROOT/'evidence/manifest.json').read_text())
    flow.append(para('Source revision: '+m['source_commit']))
    for entry in m['files']:
        flow.append(para(entry['source_path'],'Heading3'));flow.append(para(entry['source_url']));flow.append(para('SHA-256: '+entry['sha256']))
    SimpleDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=44,bottomMargin=50,title='IT Rollout Delivery Pack',author='Nazmul Hassan').build(flow,onFirstPage=footer,onLaterPages=footer)
    from pypdf import PdfReader
    reader=PdfReader(OUTPUT)
    print(f'PDF built: pack/IT-Rollout-Delivery-Pack.pdf ({len(reader.pages)} pages)')
if __name__=='__main__': main()
