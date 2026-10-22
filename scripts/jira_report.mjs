// Rebuild from the real Jira CSV export; requires the bundled @oai/artifact-tool runtime.
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';
import path from 'node:path';
const root = fileURLToPath(new URL('../', import.meta.url));
const require = createRequire(path.join(root, 'tmp', 'report-runtime.cjs'));
const {Workbook, SpreadsheetFile} = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const csv = await fs.readFile(path.join(root, 'jira/issues.csv'), 'utf8');
const imported = await Workbook.fromCSV(csv.replace(/^\uFEFF/, ''), {sheetName: 'CSV'});
const values = imported.worksheets.getItem('CSV').getUsedRange().values;
const [headers, ...data] = values;
const col = name => headers.indexOf(name);
if (data.length !== 43 || new Set(data.map(r => r[0])).size !== data.length) throw Error('Issue export count/uniqueness mismatch');
const state = JSON.parse(await fs.readFile(path.join(root, 'jira/state.json'), 'utf8'));
const exported = JSON.parse(await fs.readFile(path.join(root, 'jira/issues-api.json'), 'utf8'));
const wb = Workbook.create();
const report = wb.worksheets.add('Status');
const source = wb.worksheets.add('Issues');
for (const sheet of [report, source]) sheet.showGridLines = false;
source.getRange('A1').values = [['Source: Jira REST API export, jira/issues.csv; captured ' + exported.capturedAt]];
source.getRange('A2').values = [['Fictional case study run in a real Jira site; one row per live issue.']];
source.getRange(`A4:K${data.length+4}`).values = [headers, ...data];
source.tables.add(`A4:K${data.length+4}`, true, 'JiraIssues');
source.getRange('L4').values=[['Is risk (label)']];
for(let r=5;r<=data.length+4;r++) source.getRange(`L${r}`).formulas=[[`=IF(ISNUMBER(SEARCH(";risk;",";"&H${r}&";")),1,0)`]];
source.freezePanes.freezeRows(4);
source.getRange(`A1:K${data.length+4}`).format.font.name = 'Arial';
source.getRange(`A1:K${data.length+4}`).format.font.size = 10;
source.getRange('A:K').format.columnWidth = 20;
source.getRange('C:C').format.columnWidth = 58;
source.getRange('H:H').format.columnWidth = 50;
source.getRange('K:K').format.columnWidth = 65;
source.getRange(`A5:K${data.length+4}`).format.rowHeight = 38;
source.getRange(`A5:K${data.length+4}`).format.wrapText = true;
source.getRange(`A5:K${data.length+4}`).format.verticalAlignment = 'center';
source.getRange('A1:K2').format.rowHeight = 23;
report.getRange('A2').values = [['IT rollout | Jira status']];
report.getRange('A3').values = [['Fictional case study run in a real Jira site. Status changes are administration exercises.']];
report.getRange('A4').values = [['Captured ' + exported.capturedAt + ' | No business-user UAT or production completion claimed.']];
report.getRange('A6:H6').values = [['Epic', 'Stories', 'To Do', 'In Progress', 'In UAT', 'Done', 'Done %', 'Jira epic']];
const end = data.length + 4;
const types = `Issues!$B$5:$B$${end}`;
const statuses = `Issues!$D$5:$D$${end}`;
const epics = `Issues!$E$5:$E$${end}`;
const ratings = `Issues!$G$5:$G$${end}`;
const riskFlags = `Issues!$L$5:$L$${end}`;
const themes = Object.entries(state.issues).filter(([id]) => id.startsWith('epic-'));
for (let i=0;i<themes.length;i++) {
  const [id,key]=themes[i], row=i+7;
  report.getRange(`A${row}`).values=[[id.slice(5).replace(/^./,s=>s.toUpperCase())]];
  report.getRange(`H${row}`).values=[[key]];
  report.getRange(`B${row}`).formulas=[[`=COUNTIFS(${types},"Story",${epics},H${row})`]];
  for (const [column,status] of [['C','To Do'],['D','In Progress'],['E','In UAT'],['F','Done']]) {
    report.getRange(`${column}${row}`).formulas=[[`=COUNTIFS(${types},"Story",${epics},H${row},${statuses},"${status}")`]];
  }
  report.getRange(`G${row}`).formulas=[[`=IF(B${row}=0,0,F${row}/B${row})`]];
}
report.getRange('A12').values=[['Total stories']];
for (const column of ['B','C','D','E','F']) report.getRange(`${column}12`).formulas=[[`=SUM(${column}7:${column}11)`]];
report.getRange('G12').formulas=[['=IF(B12=0,0,F12/B12)']];
report.getRange('G7:G12').setNumberFormat('0%');
report.getRange('A15:B19').values=[['Story / UAT status','Count'],['To Do',null],['In Progress',null],['In UAT',null],['Done',null]];
for (let row=16;row<=19;row++) report.getRange(`B${row}`).formulas=[[`=COUNTIFS(${types},"Story",${statuses},A${row})`]];
report.getRange('D15:F18').values=[['Open risk rating','Open','Total'],['High',null,null],['Medium',null,null],['All risks',null,null]];
for (let row=16;row<=17;row++) {
 report.getRange(`E${row}`).formulas=[[`=COUNTIFS(${riskFlags},1,${ratings},D${row},${statuses},"<>Done")`]];
 report.getRange(`F${row}`).formulas=[[`=COUNTIFS(${riskFlags},1,${ratings},D${row})`]];
}
report.getRange('E18:F18').formulas=[['=SUM(E16:E17)','=SUM(F16:F17)']];
report.getRange('A22:D22').values=[['Risk key','Live status','Rating','Risk description']];
const risks = data.filter(r => (';'+r[col('Labels')]+';').includes(';risk;'));
report.getRange(`A23:D${22+risks.length}`).values=risks.map(r=>[r[0],r[col('Status')],r[col('Risk rating')],r[col('Summary')]]);
report.getRange('A29').values=[['Historical lab evidence is preserved in the issue descriptions; it does not establish current rollout acceptance.']];
report.getRange('A30').values=[['Refresh: export Jira issues, then rerun scripts/jira_report.mjs. Counts use the Issues sheet and exact live statuses.']];
report.getRange('A1:H30').format.font.name='Arial';
report.getRange('A1:H30').format.font.size=10;
report.getRange('A2').format.font.size=16;
report.getRange('A2').format.font.bold=true;
report.getRange('A1:H30').format.rowHeight=25;
report.getRange('A:A').format.columnWidth=25;
report.getRange('B:C').format.columnWidth=13;
report.getRange('D:D').format.columnWidth=24;
report.getRange('E:F').format.columnWidth=13;
report.getRange('G:G').format.columnWidth=12;
report.getRange('H:H').format.columnWidth=16;
for (const address of ['A6:H6','A15:B15','D15:F15','A22:D22']) {
 const range=report.getRange(address);
 range.format.fill='#203A5F';range.format.font.color='#FFFFFF';range.format.font.bold=true;
 range.format.horizontalAlignment='center';
}
report.getRange('A12:H12').format.fill='#E9EFF6';
report.getRange('A12:H12').format.font.bold=true;
// Risk descriptions span the remaining blank columns; do not merge calculation cells.
for(let row=23;row<23+risks.length;row++) {
 report.getRange(`D${row}:H${row}`).merge();report.getRange(`D${row}:H${row}`).format.wrapText=true;
 report.getRange(`A${row}:H${row}`).format.rowHeight=33;
}
const chart=report.charts.add('bar',report.getRange('A15:B19'));
chart.title='Story status (administration exercise)';chart.setPosition('I6','P20');
chart.titleTextStyle.fontSize=12;chart.titleTextStyle.typeface='Arial';
wb.recalculate();
const independent={stories:data.filter(r=>r[1]==='Story').length, risks:risks.length,
 uat:data.filter(r=>r[1]==='Story'&&r[3]==='In UAT').length};
const reconciled={stories:report.getRange('B12').values[0][0],risks:report.getRange('E18').values[0][0],uat:report.getRange('B18').values[0][0]};
console.log({independent,reconciled});
if (reconciled.stories!==independent.stories || reconciled.risks!==independent.risks || reconciled.uat!==independent.uat) throw Error('Report reconciliation failed');
// Verify formulas respond to source edits, then restore the actual exported value.
const original=source.getRange('D10').values[0][0];
source.getRange('D10').values=[['Done']];
if (report.getRange('F12').values[0][0]!==1) throw Error('Status formulas did not recalculate');
source.getRange('D10').values=[[original]];wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Formula errors'});
console.log(errors.ndjson);
console.log((await wb.inspect({kind:'table',range:'Status!A6:H19',include:'values,formulas',tableMaxRows:15,tableMaxCols:8,maxChars:3500})).ndjson);
for (const [sheetName,range,name] of [['Status','A1:P30','status-report-preview.png'],['Issues','A1:G12','issues-preview.png']]) {
 const preview=await wb.render({sheetName,range,scale:1.5,format:'png'});
 await fs.writeFile(path.join(root,'jira',name),new Uint8Array(await preview.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(path.join(root,'jira/status-report.xlsx'));
await fs.writeFile(path.join(root,'jira/report-verification.json'),JSON.stringify({source:'issues.csv',capturedAt:exported.capturedAt,independent,recalculationTest:'PASS: temporary status change restored',formulaScan:errors.ndjson},null,2)+'\n');
console.log('Exported jira/status-report.xlsx');
