from math import sin, pi
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'footer-wave.gif'
W,H=960,100
font_paths=[r'C:\Windows\Fonts\seguisb.ttf',r'C:\Windows\Fonts\arialbd.ttf']
font_path=next((path for path in font_paths if Path(path).exists()),None)
font=ImageFont.truetype(font_path,18) if font_path else ImageFont.load_default()
frames=[]
for frame in range(32):
    phase=2*pi*frame/32
    canvas=Image.new('RGB',(W,H),(8,14,10)).convert('RGBA')
    waves=Image.new('RGBA',(W,H),(0,0,0,0)); draw=ImageDraw.Draw(waves)
    colors=[(14,68,41,190),(38,166,65,220),(57,211,83,210)]
    for lane,color in enumerate(colors):
        points=[(x,65+lane*7+11*sin(x/W*2*pi+phase+lane*1.2)) for x in range(-10,W+10,8)]
        draw.line(points,fill=color,width=4 if lane==1 else 3)
    canvas=Image.alpha_composite(canvas,waves.filter(ImageFilter.GaussianBlur(5)))
    canvas=Image.alpha_composite(canvas,waves)
    d=ImageDraw.Draw(canvas)
    text='OBRIGADO POR VISITAR MEU PERFIL'
    tw=d.textlength(text,font=font)
    d.text(((W-tw)/2,16),text,font=font,fill=(166,255,180,255))
    frames.append(canvas.convert('RGB').quantize(colors=160,method=Image.Quantize.FASTOCTREE))
OUT.parent.mkdir(parents=True,exist_ok=True)
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True,disposal=2)
print(f'Created {OUT} ({OUT.stat().st_size:,} bytes, {len(frames)} frames)')
