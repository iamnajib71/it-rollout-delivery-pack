"""Stage only public showcase assets for GitHub Pages."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'tmp/site';out.mkdir(parents=True,exist_ok=True)
for name in ['index.html','docs/demo.gif','pack/IT-Rollout-Delivery-Pack.pdf']:
    dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
print('Pages site staged: index, recorded demo and PDF')
