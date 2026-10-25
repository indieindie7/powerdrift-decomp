"""trackmap.py - draw the 2048-point circuits of main.bin (0x40000 + n*0x3000) top-down, colour = height.
Run: py -3.13 -I tools/trackmap.py <main.bin> <out.png>  (local view only; the PNG is derived game data, never publish)."""
import struct, sys
from PIL import Image, ImageDraw
b = open(sys.argv[1], 'rb').read()
N, BASE, STEP = 20, 0x40000, 0x3000
tiles = []
for t in range(N):
    pts = [struct.unpack_from('>3h', b, BASE + t * STEP + i * 6) for i in range(2048)]
    xs, ys, zs = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
    S = 300
    span = max(max(xs) - min(xs), max(zs) - min(zs), 1)
    im = Image.new('RGB', (S, S + 16), (24, 26, 32)); d = ImageDraw.Draw(im)
    ylo, yhi = min(ys), max(ys)
    def P(p): return (10 + (p[0] - min(xs)) * (S - 20) / span, 10 + (max(zs) - p[2]) * (S - 20) / span)
    for i in range(2048):
        a, c = pts[i], pts[(i + 1) % 2048]
        h = (a[1] - ylo) / max(yhi - ylo, 1)
        d.line([P(a), P(c)], fill=(int(80 + 175 * h), int(200 - 120 * h), 255 - int(200 * h)), width=3)
    d.ellipse([P(pts[0])[0] - 4, P(pts[0])[1] - 4, P(pts[0])[0] + 4, P(pts[0])[1] + 4], fill=(255, 255, 255))
    d.text((4, S), '%d @%05x  y %d..%d' % (t, BASE + t * STEP, ylo, yhi), fill=(230, 230, 230))
    tiles.append(im)
W = 5
out = Image.new('RGB', (W * 300, (N + W - 1) // W * 316))
for i, im in enumerate(tiles):
    out.paste(im, ((i % W) * 300, (i // W) * 316))
out.save(sys.argv[2]); print('wrote', sys.argv[2])
