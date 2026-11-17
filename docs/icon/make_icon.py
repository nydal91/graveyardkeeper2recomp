# Graveyard Keeper Recomp's app icon (original art, nothing of the game's): a moonlit graveyard - a pale moon in an
# indigo sky, a round-topped gravestone on a mound with a shovel stuck in it, a green spirit wisp drifting by, a dead
# tree at the edge, on a rounded near-black square. The launcher's background (runtime/ui/splash.mm: keeper_art) is the
# same scene. Writes docs/icon/icon.png, the app's assets/icon.png (the window icon) and the Android mipmaps.
import math, os, random
from PIL import Image, ImageDraw, ImageFilter

S = 1024
root = os.path.dirname(os.path.abspath(__file__))
repo = os.path.dirname(os.path.dirname(root))
rnd = random.Random(1883)

def lerp(a, b, f): return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(len(a)))

def blurred(draw_fn, radius):
    layer = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    return layer.filter(ImageFilter.GaussianBlur(radius))

# sky: deep indigo above, dark teal at the horizon; ground below near-black green
HZ = 780
bg = Image.new('RGBA', (S, S))
d = ImageDraw.Draw(bg)
for y in range(S):
    if y < HZ:
        f = y / HZ
        c = lerp((10, 12, 34), (24, 44, 52), f * f)
    else:
        c = lerp((14, 22, 18), (5, 8, 6), min(1, (y - HZ) / (S - HZ)))
    d.line([(0, y), (S, y)], fill=c + (255,))

# stars
for _ in range(90):
    x, y = rnd.randint(20, S - 20), rnd.randint(20, int(HZ * 0.75))
    r = rnd.choice((1, 1, 1, 2))
    a = rnd.randint(70, 200)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 228, 255, a))

# the moon: glow, disc, a few craters
M, R = (740, 250), 130
bg = Image.alpha_composite(bg, blurred(lambda g: g.ellipse([M[0] - 300, M[1] - 300, M[0] + 300, M[1] + 300],
                                                           fill=(190, 205, 235, 90)), 90))
d = ImageDraw.Draw(bg)
d.ellipse([M[0] - R, M[1] - R, M[0] + R, M[1] + R], fill=(226, 230, 220, 255))
for cx, cy, cr in ((-40, -30, 26), (35, 20, 18), (-10, 55, 14), (55, -55, 12)):
    d.ellipse([M[0] + cx - cr, M[1] + cy - cr, M[0] + cx + cr, M[1] + cy + cr], fill=(203, 208, 198, 255))

# thin clouds drifting across the moon
bg = Image.alpha_composite(bg, blurred(lambda g: [g.ellipse([x - r, y - r * 0.22, x + r, y + r * 0.22],
                                                            fill=(16, 20, 40, 150))
                                                   for x, y, r in ((680, 300, 260), (820, 210, 200), (420, 150, 240))], 24))
d = ImageDraw.Draw(bg)

# far hill line
hill = [(0, HZ)]
for i in range(13):
    x = S * i / 12
    hill.append((x, HZ - 40 - 60 * math.sin(i * 0.9 + 1.2) ** 2 - rnd.randint(0, 24)))
hill += [(S, HZ), (S, S), (0, S)]
d.polygon(hill, fill=(10, 16, 16, 255))

# the dead tree, right edge: trunk and a few bare branches
def branch(g, x, y, ang, len_, w, depth):
    if depth == 0 or len_ < 8: return
    x2, y2 = x + math.cos(ang) * len_, y + math.sin(ang) * len_
    g.line([(x, y), (x2, y2)], fill=(6, 9, 8, 255), width=max(2, int(w)))
    for da, f in ((-0.55, 0.68), (0.4, 0.62), (-0.1, 0.8)):
        branch(g, x2, y2, ang + da + rnd.uniform(-0.12, 0.12), len_ * f, w * 0.62, depth - 1)
branch(d, 950, HZ + 30, -math.pi / 2 - 0.12, 150, 26, 5)

# the mound and the gravestone (round-topped, slightly tilted), a cross carved on it
GX, GY = 430, HZ + 40
d.ellipse([GX - 260, GY - 40, GX + 260, GY + 90], fill=(9, 14, 10, 255))
stone = Image.new('RGBA', (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(stone)
sw, sh = 190, 300
sd.rounded_rectangle([GX - sw // 2, GY - sh, GX + sw // 2, GY + 20], radius=95, fill=(36, 42, 48, 255))
sd.rectangle([GX - sw // 2, GY - 60, GX + sw // 2, GY + 20], fill=(36, 42, 48, 255))
# moonlit edge on the right
sd.rounded_rectangle([GX - sw // 2 + 14, GY - sh + 10, GX + sw // 2 - 6, GY + 10], radius=88,
                     outline=(96, 108, 116, 255), width=6)
# carved cross
sd.rectangle([GX - 14, GY - sh + 70, GX + 14, GY - 90], fill=(22, 26, 30, 255))
sd.rectangle([GX - 52, GY - sh + 108, GX + 52, GY - sh + 136], fill=(22, 26, 30, 255))
stone = stone.rotate(-4, center=(GX, GY), resample=Image.BICUBIC)
bg = Image.alpha_composite(bg, stone)
d = ImageDraw.Draw(bg)

# the shovel stuck in the mound, left of the stone: handle, grip, blade
SX = GX - 190
d.line([(SX, HZ - 200), (SX + 40, GY + 10)], fill=(58, 42, 28, 255), width=16)
d.rounded_rectangle([SX - 34, HZ - 236, SX + 34, HZ - 196], radius=16, outline=(58, 42, 28, 255), width=14)
d.polygon([(SX + 18, GY - 40), (SX + 78, GY - 20), (SX + 62, GY + 46), (SX + 30, GY + 40)], fill=(70, 76, 84, 255))

# a green spirit wisp: glow and a bright core with a tail
W = (640, 560)
bg = Image.alpha_composite(bg, blurred(lambda g: g.ellipse([W[0] - 110, W[1] - 110, W[0] + 110, W[1] + 110],
                                                           fill=(70, 220, 140, 120)), 46))
bg = Image.alpha_composite(bg, blurred(lambda g: g.ellipse([W[0] - 34, W[1] - 34, W[0] + 34, W[1] + 34],
                                                           fill=(180, 255, 210, 255)), 10))
d = ImageDraw.Draw(bg)
for i in range(7):  # tail drifting down-left
    f = i / 7
    x, y, r = W[0] - 40 * f - 10 * math.sin(f * 5), W[1] + 60 * f, 16 * (1 - f) + 3
    d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 240, 170, int(160 * (1 - f))))

# ground fog
bg = Image.alpha_composite(bg, blurred(lambda g: [g.ellipse([x - r, HZ - 20 - r * 0.14, x + r, HZ - 20 + r * 0.14],
                                                            fill=(60, 80, 84, 70))
                                                   for x, r in ((200, 300), (560, 360), (900, 280))], 30))

# rounded near-black square mask, a faint inner border
mask = Image.new('L', (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, S, S], radius=190, fill=255)
out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
out.paste(bg, (0, 0), mask)
d = ImageDraw.Draw(out)
d.rounded_rectangle([6, 6, S - 6, S - 6], radius=184, outline=(70, 90, 96, 120), width=4)

out.save(os.path.join(root, 'icon.png'))
out.save(os.path.join(repo, 'app', 'src', 'main', 'assets', 'icon.png'))
for dpi, size in (('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)):
    p = os.path.join(repo, 'app', 'src', 'main', 'res', f'mipmap-{dpi}')
    os.makedirs(p, exist_ok=True)
    out.resize((size, size), Image.LANCZOS).save(os.path.join(p, 'ic_launcher.png'))
print('icon written')
