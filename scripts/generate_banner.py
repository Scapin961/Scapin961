from math import sin, pi
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "banner.gif"
W, H = 960, 240
FRAMES, DURATION = 36, 85
FONT_PATHS = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\seguisb.ttf"]
font_path = next((path for path in FONT_PATHS if Path(path).exists()), None)
name_font = ImageFont.truetype(font_path, 82) if font_path else ImageFont.load_default()
small_font = ImageFont.truetype(font_path, 16) if font_path else ImageFont.load_default()
name = "SCAPIN"
letter_gap = 8
widths = [name_font.getlength(char) for char in name]
name_width = sum(widths) + letter_gap * (len(name) - 1)
start_x = (W - name_width) / 2
frames = []

for frame_index in range(FRAMES):
    phase = 2 * pi * frame_index / FRAMES
    base = Image.new("RGB", (W, H))
    pixels = base.load()
    for y in range(H):
        for x in range(W):
            t = y / H
            glow = max(0, 1 - abs(x - W * 0.52) / (W * 0.75))
            pixels[x, y] = (int(7 + 5 * glow), int(14 + 11 * (1 - t)), int(9 + 7 * glow))

    # Soft, layered waves behind the lettering.
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    wave_colors = [(14, 68, 41, 155), (38, 166, 65, 145), (57, 211, 83, 125)]
    for lane, color in enumerate(wave_colors):
        points = []
        for x in range(-10, W + 10, 8):
            y = 174 + lane * 10 + 17 * sin((x / W) * 2 * pi + phase + lane * 1.25)
            points.append((x, y))
        gdraw.line(points, fill=color, width=5 if lane == 0 else 3)
    wave_lines = glow_layer.copy()
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(9))
    base = Image.alpha_composite(base.convert("RGBA"), glow_layer)
    base = Image.alpha_composite(base, wave_lines)
    draw = ImageDraw.Draw(base)

    # Tiny ambient stars.
    for n in range(22):
        x = (n * 137 + 47) % W
        y = (n * 53 + 29) % 155
        alpha = int(90 + 70 * (0.5 + 0.5 * sin(phase + n)))
        draw.ellipse((x, y, x + 2, y + 2), fill=(57, 211, 83, alpha))

    # Per-letter vertical motion creates the wave through the name.
    x = start_x
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    for i, (char, char_width) in enumerate(zip(name, widths)):
        offset = 9 * sin(phase - i * 0.72)
        pulse = 0.5 + 0.5 * sin(phase + i * 0.6)
        green = int(150 + 105 * pulse)
        color = (int(28 + 45 * pulse), green, int(55 + 35 * pulse), 255)
        td.text((x, 42 + offset), char, font=name_font, fill=color, stroke_width=1, stroke_fill=(170, 255, 185, 210))
        x += char_width + letter_gap
    text_glow = text_layer.filter(ImageFilter.GaussianBlur(12))
    base = Image.alpha_composite(base, text_glow)
    base = Image.alpha_composite(base, text_layer)
    draw = ImageDraw.Draw(base)

    tagline = "FULL STACK DEVELOPER  |  WEB & MOBILE"
    tagline_width = draw.textlength(tagline, font=small_font)
    draw.text(((W - tagline_width) / 2, 148), tagline, font=small_font, fill=(166, 255, 180, 255))
    draw.rounded_rectangle((W / 2 - 88, 178, W / 2 + 88, 181), radius=2, fill=(57, 211, 83, 230))
    frames.append(base.convert("RGB").quantize(colors=192, method=Image.Quantize.FASTOCTREE))

OUT.parent.mkdir(parents=True, exist_ok=True)
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True, disposal=2)
print(f"Created {OUT} ({OUT.stat().st_size:,} bytes, {FRAMES} frames)")
