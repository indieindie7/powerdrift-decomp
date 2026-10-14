"""satnew.py <main.bin> <CRS_N.DAT> [out.png]: compare the CRS_N circuits that are not arcade circuits with every arcade circuit
(per-point equal count, mean distance after best cyclic shift on a 64-point sample), print stats; optional side-by-side drawing
of each new circuit and its nearest arcade circuit (local view only; derived game data, never publish)."""
import sys, struct
main = open(sys.argv[1], 'rb').read(); n = open(sys.argv[2], 'rb').read()
L = lambda b, o: struct.unpack_from('>I', b, o)[0]
pts = lambda b, o: [struct.unpack_from('>3h', b, o + i * 6) for i in range(2048)]
arc = {}
for i in range(29):
    r = L(main, 0x385d6 + i * 4); c = L(main, r)
    arc.setdefault(c, i)
for b in [0x40000 + k * 0x3000 for k in range(20)]:
    arc.setdefault(b, -1)
arcp = {c: pts(main, c) for c in arc}
subs, o = [], 0
while True:
    v = L(n, o)
    if v >= len(n) or (subs and v <= subs[-1]): break
    subs.append(v); o += 4
res = []
for s in subs:
    p = pts(n, s + 0x18)
    if any(p[:4] == q[:4] for q in arcp.values()): continue
    xs, ys, zs = zip(*p)
    best = []
    for c, q in arcp.items():
        eq = sum(1 for a, b in zip(p, q) if a == b)
        eqset = len(set(p) & set(q))
        d = min(sum(abs(p[j][0] - q[(j + sh) % 2048][0]) + abs(p[j][2] - q[(j + sh) % 2048][2]) for j in range(0, 2048, 32))
                for sh in range(0, 2048, 16)) / 64
        best.append((d, c, eq, eqset))
    best.sort()
    print('CRS_N +%x: x %d..%d y %d..%d z %d..%d' % (s, min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
    for d, c, eq, eqset in best[:3]:
        print('   arcade %05x (entry %d): same index %d, shared points %d, mean xz dist %.0f' % (c, arc[c], eq, eqset, d))
    res.append((s, p, best[0][1]))
if len(sys.argv) > 3:
    from PIL import Image, ImageDraw
    S = 300
    im = Image.new('RGB', (2 * S, len(res) * (S + 16)), (24, 26, 32)); d = ImageDraw.Draw(im)
    for r, (s, p, c) in enumerate(res):
        for col, (q, lab) in enumerate([(p, 'CRS_N +%x' % s), (arcp[c], 'arcade %05x' % c)]):
            xs, ys, zs = zip(*q); span = max(max(xs) - min(xs), max(zs) - min(zs), 1)
            P = lambda t: (col * S + 10 + (t[0] - min(xs)) * (S - 20) / span, r * (S + 16) + 10 + (max(zs) - t[2]) * (S - 20) / span)
            for i in range(2048):
                h = (q[i][1] - min(ys)) / max(max(ys) - min(ys), 1)
                d.line([P(q[i]), P(q[(i + 1) % 2048])], fill=(int(80 + 175 * h), int(200 - 120 * h), 255 - int(200 * h)), width=3)
            d.text((col * S + 4, r * (S + 16) + S), lab, fill=(230, 230, 230))
    im.save(sys.argv[3])
