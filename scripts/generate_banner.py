from math import cos, sin, pi
from pathlib import Path
from random import Random
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'banner.gif'
W,H=960,280
FRAMES,DURATION=72,70
EDGE_COLOR=(13,17,23)
EDGE_FADE_X=110
EDGE_FADE_Y=18
FONT_PATHS=[r'C:\Windows\Fonts\arialbd.ttf',r'C:\Windows\Fonts\seguisb.ttf']
font_path=next((p for p in FONT_PATHS if Path(p).exists()),None)
name_font=ImageFont.truetype(font_path,104) if font_path else ImageFont.load_default()
name='SCAPIN'
letter_gap=5
center=(W//2,132)

def smooth(v):
    v=max(0.0,min(1.0,v))
    return int(255*(v*v*(3-2*v)))

def blend_edges(image):
    im=image.convert('RGB')
    mx=Image.new('L',(W,1)); mxp=mx.load()
    for x in range(W): mxp[x,0]=smooth(min(x,W-1-x)/EDGE_FADE_X)
    my=Image.new('L',(1,H)); myp=my.load()
    for y in range(H): myp[0,y]=smooth(min(y,H-1-y)/EDGE_FADE_Y)
    mask=ImageChops.darker(mx.resize((W,H),Image.Resampling.NEAREST),my.resize((W,H),Image.Resampling.NEAREST))
    return Image.composite(im,Image.new('RGB',(W,H),EDGE_COLOR),mask)

# Deep black-green background with a restrained grid.
background=Image.new('RGBA',(W,H),(6,12,8,255)); bd=ImageDraw.Draw(background)
for y in range(H):
    lift=int(7*(1-abs(y-H*0.5)/(H*0.5)))
    bd.line((0,y,W,y),fill=(6+lift//2,12+lift,8+lift//2,255))
for x in range(80,W,80): bd.line((x,30,x,250),fill=(13,31,18,80),width=1)
for y in range(54,250,40): bd.line((46,y,914,y),fill=(13,31,18,65),width=1)
rng=Random(961)
for _ in range(30):
    x,y=rng.randrange(24,W-24),rng.randrange(16,H-16)
    bd.ellipse((x,y,x+2,y+2),fill=(57,211,83,rng.randrange(55,135)))

# Place each letter separately so the reveal can travel outward one letter at a time.
advances=[name_font.getlength(ch) for ch in name]
total=sum(advances)+letter_gap*(len(name)-1)
cursor=(W-total)/2
letter_masks=[]
for ch,advance in zip(name,advances):
    mask=Image.new('L',(W,H),0); md=ImageDraw.Draw(mask)
    bounds=name_font.getbbox(ch,stroke_width=1)
    x=int(cursor-bounds[0]); y=int(82-bounds[1])
    md.text((x,y),ch,font=name_font,fill=255,stroke_width=1,stroke_fill=255)
    bbox=mask.getbbox()
    letter_masks.append((mask,bbox))
    cursor+=advance+letter_gap
word_center=(letter_masks[0][1][0]+letter_masks[-1][1][2])/2
full_name_mask=Image.new('L',(W,H),0)
for letter_mask,_ in letter_masks:
    full_name_mask=ImageChops.lighter(full_name_mask,letter_mask)
reveal_order=sorted(range(len(name)),key=lambda i:(abs((letter_masks[i][1][0]+letter_masks[i][1][2])/2-word_center),letter_masks[i][1][0]))
sequence_position={letter_index:order for order,letter_index in enumerate(reveal_order)}
all_done_frame=10+(len(name)-1)*7+6

rays=[]; rng=Random(47)
for i in range(40):
    angle=(2*pi*i/40)+rng.uniform(-0.035,0.035)
    rays.append((angle,rng.uniform(155,470),rng.choice([1,1,2,2,3])))

def electric_bolt(draw,x,y_top,y_bottom,seed,side):
    rng=Random(seed)
    points=[]
    y=y_top
    while y<y_bottom:
        points.append((x+rng.randint(-5,5),y))
        y+=rng.randint(7,12)
    points.append((x+rng.randint(-4,4),y_bottom))
    draw.line(points,fill=(185,255,196,245),width=2)
    for j in range(1,len(points)-1,2):
        px,py=points[j]
        branch=[(px,py),(px+side*rng.randint(5,11),py+rng.randint(3,7)),(px+side*rng.randint(10,18),py+rng.randint(8,14))]
        draw.line(branch,fill=(85,255,115,220),width=1)

frames=[]
for frame in range(FRAMES):
    phase=2*pi*frame/FRAMES
    canvas=background.copy()
    energy=Image.new('RGBA',(W,H),(0,0,0,0)); ed=ImageDraw.Draw(energy)
    panel_alpha=min(205,35+frame*10)
    ed.rounded_rectangle((46,26,914,252),radius=22,outline=(38,166,65,panel_alpha),width=2)
    for x,y,dx,dy in [(46,26,1,1),(914,26,-1,1),(46,252,1,-1),(914,252,-1,-1)]:
        ed.line((x,y+dy*30,x,y,x+dx*30,y),fill=(57,211,83,panel_alpha),width=4)

    # Electric rays expand from the panel's core before the letters begin to form.
    ray_progress=max(0.0,min(1.0,(frame-3)/18))
    if ray_progress:
        for i,(angle,distance,width) in enumerate(rays):
            reach=distance*ray_progress
            x2=center[0]+cos(angle)*reach
            y2=center[1]+sin(angle)*reach*0.43
            pulse=0.5+0.5*sin(phase*2+i*0.7)
            alpha=int((85+135*pulse)*ray_progress)
            color=(57,211,83,alpha) if i%3 else (165,255,176,alpha)
            ed.line((center[0],center[1],x2,y2),fill=color,width=width)
            if i%4==0 and ray_progress>0.3:
                sx=center[0]+cos(angle)*reach*0.55; sy=center[1]+sin(angle)*reach*0.55*0.43
                bx=sx+cos(angle+0.18)*reach*0.16; by=sy+sin(angle+0.18)*reach*0.16*0.43
                ed.line((sx,sy,bx,by),fill=(38,166,65,alpha//2),width=1)

    canvas=Image.alpha_composite(canvas,energy.filter(ImageFilter.GaussianBlur(8)))
    canvas=Image.alpha_composite(canvas,energy)

    letters_layer=Image.new('RGBA',(W,H),(0,0,0,0))
    letters_glow=Image.new('RGBA',(W,H),(0,0,0,0))
    ld=ImageDraw.Draw(letters_layer); gd=ImageDraw.Draw(letters_glow)
    sparks=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sparks)
    active_count=0
    for i,(mask,bbox) in enumerate(letter_masks):
        order=sequence_position[i]
        start=10+order*7
        progress=max(0.0,min(1.0,(frame-start)/6))
        if progress<=0: continue
        active_count+=1
        x0,y0,x1,y1=bbox
        width=max(1,x1-x0)
        letter_center=(x0+x1)/2
        if letter_center<word_center:
            cutoff=x1-int(width*progress)
            clip=Image.new('L',(W,H),0); ImageDraw.Draw(clip).rectangle((cutoff,y0-2,x1+2,y1+2),fill=255)
            scan_x=cutoff; bolt_side=-1
        else:
            cutoff=x0+int(width*progress)
            clip=Image.new('L',(W,H),0); ImageDraw.Draw(clip).rectangle((x0-2,y0-2,cutoff,y1+2),fill=255)
            scan_x=cutoff; bolt_side=1
        visible=ImageChops.multiply(mask,clip)
        ld.bitmap((0,0),Image.new('RGBA',(W,H),(57,211,83,0))) if False else None
        color=Image.new('RGBA',(W,H),(57,211,83,0))
        color.putalpha(visible)
        letters_layer=Image.alpha_composite(letters_layer,color)
        glowmask=visible.filter(ImageFilter.GaussianBlur(12))
        gc=Image.new('RGBA',(W,H),(57,211,83,0)); gc.putalpha(glowmask.point(lambda a:a*130//255))
        letters_glow=Image.alpha_composite(letters_glow,gc)
        if progress<1:
            electric_bolt(sd,scan_x,y0-13,y1+13,frame*97+i*503,bolt_side)
            # Spark burst traces from the source to the active letter edge.
            sd.line((center[0],center[1],scan_x, (y0+y1)//2),fill=(108,255,130,180),width=1)
            for j in range(4):
                sx=scan_x+Random(frame*37+i*23+j).randint(-9,9)
                sy=Random(frame*41+i*29+j).randint(y0-8,y1+8)
                sd.ellipse((sx-2,sy-2,sx+2,sy+2),fill=(205,255,210,230))

    canvas=Image.alpha_composite(canvas,letters_glow)
    canvas=Image.alpha_composite(canvas,letters_layer)
    if active_count and frame<all_done_frame:
        canvas=Image.alpha_composite(canvas,sparks.filter(ImageFilter.GaussianBlur(3)))
        canvas=Image.alpha_composite(canvas,sparks)

    # The source core flashes during the reveal, then breathes quietly in the panel.
    core=Image.new('RGBA',(W,H),(0,0,0,0)); cd=ImageDraw.Draw(core)
    pulse=0.5+0.5*sin(phase*2)
    radius=int(5+10*pulse) if frame<all_done_frame else int(3+3*pulse)
    cd.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),fill=(180,255,190,225))
    cd.ellipse((center[0]-radius*2,center[1]-radius*2,center[0]+radius*2,center[1]+radius*2),outline=(57,211,83,135),width=2)
    canvas=Image.alpha_composite(canvas,core.filter(ImageFilter.GaussianBlur(6)))

    if frame>=all_done_frame:
        final_name=Image.new('RGBA',(W,H),(57,211,83,0))
        final_name.putalpha(full_name_mask)
        canvas=Image.alpha_composite(canvas,final_name)
    frames.append(blend_edges(canvas).quantize(colors=192,method=Image.Quantize.FASTOCTREE))

OUT.parent.mkdir(parents=True,exist_ok=True)
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=DURATION,loop=0,optimize=True,disposal=2)
print(f'Created {OUT} ({OUT.stat().st_size:,} bytes, {FRAMES} frames)')
