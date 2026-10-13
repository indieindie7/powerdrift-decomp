"""coursemap.py - draw every circuit by course from the course table at main 0x385d6 (5 courses x 6 slots, last slot of E absent),
plus the 0x40000-block circuits no table entry uses. Colour = height, white dot = point 0.
Run: py -3.13 -I tools/coursemap.py <main.bin> <out.png>  (local view only; derived game data, never publish)."""
import struct, sys
from PIL import Image, ImageDraw
b = open(sys.argv[1], 'rb').read()
L = lambda a: struct.unpack_from('>I', b, a)[0]
S = 260

def tile(base, label):
    pts = [struct.unpack_from('>3h', b, base + i * 6) for i in range(2048)]
    xs, ys, zs = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
    span = max(max(xs) - min(xs), max(zs) - min(zs), 1)
    im = Image.new('RGB', (S, S + 16), (24, 26, 32)); d = ImageDraw.Draw(im)
    ylo, yhi = min(ys), max(ys)
    def P(p): return (10 + (p[0] - min(xs)) * (S - 20) / span, 10 + (max(zs) - p[2]) * (S - 20) / span)
    for i in range(2048):
        a, c = pts[i], pts[(i + 1) % 2048]
        h = (a[1] - ylo) / max(yhi - ylo, 1)
        d.line([P(a), P(c)], fill=(int(80 + 175 * h), int(200 - 120 * h), 255 - int(200 * h)), width=3)
    x, y = P(pts[0]); d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255))
    d.text((4, S), '%s @%05x y..%d' % (label, base, yhi), fill=(230, 230, 230))
    return im

rows, used = [], set()
for c in range(5):
    row = []
    for s in range(6):
        i = c * 6 + s
        if i >= 29: row.append(None); continue
        t = L(L(0x385d6 + i * 4)); used.add(t)
        row.append(tile(t, '%s%s' % ('ABCDE'[c], 'bonus' if s == 5 else s + 1)))
    rows.append(row)
rows.append([tile(0x40000 + n * 0x3000, 'unused %d' % n) for n in range(20) if 0x40000 + n * 0x3000 not in used])
W = 6
out = Image.new('RGB', (W * S, len(rows) * (S + 16)), (10, 10, 12))
for r, row in enumerate(rows):
    for k, im in enumerate(row):
        if im: out.paste(im, (k * S, r * (S + 16)))
out.save(sys.argv[2]); print('wrote', sys.argv[2])
