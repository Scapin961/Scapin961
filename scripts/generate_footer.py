from math import sin, pi
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'footer-wave.gif'
W,H=960,100
FRAMES,DURATION=32,90
EDGE_COLOR=(13,17,23)
EDGE_FADE_X=90
EDGE_FADE_Y=12
FONT_PATHS=[r'C:\Windows\Fonts\seguisb.ttf',r'C:\Windows\Fonts\arialbd.ttf']
font_path=next((p for p in FONT_PATHS if Path(p).exists()),None)
font=ImageFont.truetype(font_path,18) if font_path else ImageFont.load_default()

def smooth(v):
    v=max(0.0,min(1.0,v)); return int(255*(v*v*(3-2*v)))

def blend_edges(image):
    mx=Image.new('L',(W,1)); px=mx.load()
    for x in range(W): px[x,0]=smooth(min(x,W-1-x)/EDGE_FADE_X)
    my=Image.new('L',(1,H)); py=my.load()
    for y in range(H): py[0,y]=smooth(min(y,H-1-y)/EDGE_FADE_Y)
    mask=ImageChops.darker(mx.resize((W,H),Image.Resampling.NEAREST),my.resize((W,H),Image.Resampling.NEAREST))
    return Image.composite(image.convert('RGB'),Image.new('RGB',(W,H),EDGE_COLOR),mask)

frames=[]
for frame in range(FRAMES):
    phase=2*pi*frame/FRAMES
    canvas=Image.new('RGBA',(W,H),(8,14,10,255))
    waves=Image.new('RGBA',(W,H),(0,0,0,0)); draw=ImageDraw.Draw(waves)
    colors=[(14,68,41,190),(38,166,65,220),(57,211,83,210)]
    for lane,color in enumerate(colors):
        points=[(x,65+lane*7+11*sin(x/W*2*pi+phase+lane*1.2)) for x in range(-10,W+10,8)]
        draw.line(points,fill=color,width=4 if lane==1 else 3)
    canvas=Image.alpha_composite(canvas,waves.filter(ImageFilter.GaussianBlur(5)))
    canvas=Image.alpha_composite(canvas,waves)
    d=ImageDraw.Draw(canvas); text='OBRIGADO POR VISITAR MEU PERFIL'; tw=d.textlength(text,font=font)
    d.text(((W-tw)/2,16),text,font=font,fill=(166,255,180,255))
    frames.append(blend_edges(canvas).quantize(colors=160,method=Image.Quantize.FASTOCTREE))
OUT.parent.mkdir(parents=True,exist_ok=True)
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=DURATION,loop=0,optimize=True,disposal=2)
print(f'Created {OUT} ({OUT.stat().st_size:,} bytes, {FRAMES} frames)')
