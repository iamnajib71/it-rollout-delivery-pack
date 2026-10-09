"""Build a typography-based 1280x640 GitHub social preview."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
def font(size):
    for p in ['C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default(size=size)
def main():
    im=Image.new('RGB',(1280,640),'#0b1523');d=ImageDraw.Draw(im)
    d.rectangle((0,0,16,640),fill='#73dfd8')
    d.text((70,55),'NAZMUL HASSAN / PORTFOLIO',font=font(25),fill='#73dfd8')
    d.text((70,120),'IT Rollout',font=font(76),fill='white')
    d.text((70,214),'Delivery Pack',font=font(76),fill='white')
    d.text((74,320),'Project Coordinator | PMO Analyst | Business Analyst',font=font(29),fill='#b7c7d9')
    for x,number,label in [(74,'25','stories with proof'),(450,'3','faults repaired'),(826,'6','monitors UP')]:
        d.rounded_rectangle((x,398,x+325,545),radius=12,fill='#16324f')
        d.text((x+22,406),number,font=font(52),fill='#73dfd8')
        d.text((x+22,484),label,font=font(25),fill='white')
    d.text((74,585),'Fictional 15-person office / Real historical homelab evidence',font=font(23),fill='#aebdd0')
    (ROOT/'docs').mkdir(exist_ok=True);im.save(ROOT/'docs/social-preview.png')
    print('Social preview built: 1280x640')
if __name__=='__main__':main()
