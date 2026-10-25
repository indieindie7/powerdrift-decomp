"""ptscan.py - split main.bin 0x40000.. into runs of (x,y,z) signed-word triples with small steps (exploration)."""
import struct, sys
b = open(sys.argv[1], 'rb').read()
lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
lim = int(sys.argv[4]) if len(sys.argv) > 4 else 0x200
p, start, prev = lo, lo, None
def sw(a): return struct.unpack_from('>h', b, a)[0]
runs = []
while p + 6 <= hi:
    t = (sw(p), sw(p + 2), sw(p + 4))
    if prev and max(abs(t[i] - prev[i]) for i in range(3)) > lim:
        runs.append((start, p)); start = p
    prev = t; p += 6
runs.append((start, p))
for s, e in runs:
    n = (e - s) // 6
    if n >= 8:
        print('%06x-%06x %5d pts first %s last %s' % (s, e, n, tuple(sw(s + 2 * i) for i in range(3)), tuple(sw(e - 6 + 2 * i) for i in range(3))))
