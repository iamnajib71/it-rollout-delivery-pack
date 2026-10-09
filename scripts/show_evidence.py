"""A small, useful terminal review view of the pack's pinned evidence."""
from pathlib import Path
import csv, argparse
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--story');args=parser.parse_args()
    if args.story:
        with (ROOT/'business-analysis/traceability.csv').open(newline='',encoding='utf-8') as f:
            matches=[r for r in csv.DictReader(f) if r['Story ID']==args.story]
        if not matches:parser.error('Unknown story ID')
        for row in matches:
            for key in ['Story ID','Requirement ID','UAT ID','Homelab test / case','Evidence file','Exact proof','Limit']:print(f'{key}: {row[key]}')
    else:
        print('HISTORICAL LAB EVIDENCE | 6 October 2026 | Australia/Sydney')
        for p in sorted((ROOT/'evidence/homelab/docs/evidence').glob('*.txt')):
            print('\n'+p.name)
            for line in p.read_text(encoding='utf-8-sig').splitlines():
                if line.startswith('RESULT:') or '6 monitors, all UP' in line:print(line)
        print('\nReal-office go-live: HOLD (physical print, restore and staffed UAT unproven)')
if __name__=='__main__':main()
