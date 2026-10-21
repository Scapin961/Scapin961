from math import sin, pi
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'tools-animated.gif'
W,H=960,210
FRAMES,DURATION=54,80
EDGE_COLOR=(13,17,23)
EDGE_FADE_X=30
EDGE_FADE_Y=18
FONT_PATHS=[r'C:\Windows\Fonts\arialbd.ttf',r'C:\Windows\Fonts\seguisb.ttf']
font_path=next((p for p in FONT_PATHS if Path(p).exists()),None)
label_font=ImageFont.truetype(font_path,15) if font_path else ImageFont.load_default()
items=[('JavaScript','#F7DF1E','javascript'),('TypeScript','#3178C6','typescript'),('Vue.js','#41B883','vuejs'),('C#','#512BD4','csharp'),('HTML5','#E34F26','html5'),('CSS3','#1572B6','css3')]
CARD_W,CARD_H,GAP=134,158,18
LEFT=(W-(len(items)*CARD_W+(len(items)-1)*GAP))//2
TOP=24

def smooth(v):
    v=max(0.0,min(1.0,v)); return int(255*(v*v*(3-2*v)))

def blend_edges(image):
    im=image.convert('RGB')
    mx=Image.new('L',(W,1)); px=mx.load()
    for x in range(W): px[x,0]=smooth(min(x,W-1-x)/EDGE_FADE_X)
    my=Image.new('L',(1,H)); py=my.load()
    for y in range(H): py[0,y]=smooth(min(y,H-1-y)/EDGE_FADE_Y)
    mask=ImageChops.darker(mx.resize((W,H),Image.Resampling.NEAREST),my.resize((W,H),Image.Resampling.NEAREST))
    return Image.composite(im,Image.new('RGB',(W,H),EDGE_COLOR),mask)

def center_text(draw,point,text,font,fill):
    box=draw.textbbox((0,0),text,font=font)
    draw.text((point[0]-(box[2]-box[0])/2,point[1]-(box[3]-box[1])/2-box[1]),text,font=font,fill=fill)

def icon_image(kind):
    path=ROOT/'assets'/'icons'/f'{kind}.png'
    with Image.open(path) as source:
        return source.convert('RGBA')

background=Image.new('RGBA',(W,H),(7,13,9,255)); bd=ImageDraw.Draw(background)
for y in range(H):
    lift=int(5*(1-abs(y-H/2)/(H/2))); bd.line((0,y,W,y),fill=(7+lift//2,13+lift,9+lift//2,255))
bd.line((28,193,W-28,193),fill=(18,52,26,255),width=1)
icons=[icon_image(kind) for _,color,kind in items]
frames=[]
for frame in range(FRAMES):
    phase=2*pi*frame/FRAMES; canvas=background.copy(); draw=ImageDraw.Draw(canvas)
    for idx,(label,color,_) in enumerate(items):
        x=LEFT+idx*(CARD_W+GAP); y=TOP; start=3+idx*5
        progress=max(0,min(1,(frame-start)/7))
        if progress>0:
            ease=1-(1-progress)**3
            bounce=1+0.12*sin(progress*pi) if progress<1 else 1
            slide=int(16*(1-ease))
            y_now=y+slide
            draw.rounded_rectangle((x,y_now,x+CARD_W,y_now+CARD_H),radius=18,fill=(12,20,14,255),outline=(29,73,39,255),width=2)
            glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
            alpha=int(60+55*(0.5+0.5*sin(phase*2+idx)))
            gd.rounded_rectangle((x-2,y_now-2,x+CARD_W+2,y_now+CARD_H+2),radius=19,outline=(57,211,83,alpha),width=3)
            canvas=Image.alpha_composite(canvas,glow.filter(ImageFilter.GaussianBlur(8)))
            draw=ImageDraw.Draw(canvas)
            draw.rounded_rectangle((x,y_now,x+CARD_W,y_now+CARD_H),radius=18,fill=(12,20,14,255),outline=(38,166,65,255),width=2)
            size=max(1,int(70*ease*bounce)); icon=icons[idx].resize((size,size),Image.Resampling.LANCZOS)
            px=int(x+(CARD_W-size)/2); py=int(y_now+17+(70-size)/2)
            canvas.alpha_composite(icon,(px,py)); draw=ImageDraw.Draw(canvas)
            text_alpha=int(255*max(0,min(1,(progress-0.38)*2.4)))
            center_text(draw,(x+CARD_W/2,y_now+123),label,label_font,(230,239,232,text_alpha))
            if progress<1:
                # A brand-colored ring and sparks emphasize each card's entrance.
                burst=Image.new('RGBA',(W,H),(0,0,0,0)); bd=ImageDraw.Draw(burst)
                radius=int(34+48*ease)
                ring_alpha=int(175*(1-progress))
                bd.ellipse((x+CARD_W/2-radius,y_now+53-radius,x+CARD_W/2+radius,y_now+53+radius),outline=(*tuple(bytes.fromhex(color.lstrip('#'))),ring_alpha),width=2)
                for ray in range(8):
                    angle=ray*pi/4+idx*0.35
                    cx=x+CARD_W/2+sin(angle)*radius
                    cy=y_now+53+sin(angle+pi/2)*radius
                    bd.ellipse((cx-2,cy-2,cx+2,cy+2),fill=(245,255,249,ring_alpha))
                canvas=Image.alpha_composite(canvas,burst.filter(ImageFilter.GaussianBlur(3)))
                canvas=Image.alpha_composite(canvas,burst)
    frames.append(blend_edges(canvas))
# One shared palette prevents palette shifts and scanline artifacts between GIF frames.
palette_samples=Image.new('RGB',(W,H*len(frames)))
for idx,frame_image in enumerate(frames):
    palette_samples.paste(frame_image,(0,idx*H))
palette=palette_samples.quantize(colors=256,method=Image.Quantize.FASTOCTREE)
frames=[frame_image.quantize(palette=palette,dither=Image.Dither.NONE) for frame_image in frames]
OUT.parent.mkdir(parents=True,exist_ok=True)
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=DURATION,loop=0,optimize=False,disposal=2)
print(f'Created {OUT} ({OUT.stat().st_size:,} bytes, {FRAMES} frames)')
