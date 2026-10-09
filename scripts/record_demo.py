"""Record real subprocess output in asciicast v2 and render a local terminal GIF.

No Docker commands are run and no synthetic test results are generated.
"""
from pathlib import Path
import json, subprocess, sys, time, textwrap
import argparse
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
def font(size):
    for p in ['C:/Windows/Fonts/consola.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default(size=size)
def render(text):
    im=Image.new('RGB',(1280,720),'#0b1523');d=ImageDraw.Draw(im)
    d.rounded_rectangle((24,24,1256,696),radius=16,fill='#132237',outline='#344c69',width=2)
    d.text((48,43),'IT ROLLOUT DELIVERY PACK | Actual local command output',font=font(23),fill='#73dfd8')
    d.text((48,79),'Fictional office / historical evidence from 6 October 2026',font=font(17),fill='#aebdd0')
    lines=[]
    for line in text.splitlines():lines.extend(textwrap.wrap(line,103) or [''])
    for i,line in enumerate(lines[-23:]):d.text((48,124+i*23),line,font=font(19),fill='#f0f5fa' if not line.startswith('>') else '#f5cf78')
    return im
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--agg',help='Optional path to asciinema agg executable');args=parser.parse_args()
    docs=ROOT/'docs';docs.mkdir(exist_ok=True)
    events=[];frames=[];durations=[];start=time.monotonic()
    commands=[('python scripts/validate.py --core',[sys.executable,'scripts/validate.py','--core']),('python scripts/build_pdf.py',[sys.executable,'scripts/build_pdf.py']),('python scripts/show_evidence.py',[sys.executable,'scripts/show_evidence.py']),('python scripts/show_evidence.py --story US-19',[sys.executable,'scripts/show_evidence.py','--story','US-19'])]
    for display,command_args in commands:
        before=time.monotonic();event_time=before-start
        output=subprocess.run(command_args,cwd=ROOT,capture_output=True,text=True,check=True)
        text='> '+display+'\n\n'+output.stdout.strip()
        if output.stderr:text+='\n'+output.stderr
        events.append([round(event_time,3),'o','\x1b[2J\x1b[H'+text.replace('\n','\r\n')+'\r\n'])
        frame=render(text);frames.append(frame)
        # Retain each real output on screen, like a paced terminal walkthrough.
        hold=8.75;elapsed=time.monotonic()-before
        if elapsed<hold:time.sleep(hold-elapsed)
        durations.append(round((time.monotonic()-before)*1000/10)*10)
    elapsed=time.monotonic()-start
    events.append([round(elapsed,3),'o','\r\nRecording complete.\r\n'])
    header={'version':2,'width':103,'height':27,'timestamp':int(time.time()),'env':{'TERM':'xterm-256color'},'title':'Real delivery pack commands; historical lab evidence'}
    (docs/'demo.cast').write_text('\n'.join(json.dumps(v) for v in [header,*events])+'\n')
    frames[0].save(docs/'demo.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
    if args.agg:
        subprocess.run([args.agg,'--idle-time-limit','20','--last-frame-duration','1','--theme','github-dark','--font-size','18',str(docs/'demo.cast'),str(docs/'demo.gif')],check=True)
    print(f'Recorded actual commands: {elapsed:.1f}s; docs/demo.cast and docs/demo.gif')
if __name__=='__main__':main()
