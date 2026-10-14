"""satcrs.py <main.bin> <saturn cd dir>: decode the Saturn CRS_x/ADV_x sub-block headers and find where each arcade
per-track block (course record pointers, NOTES "Course table" / "Per-track data") sits inside the matching Saturn sub-block."""
import sys, os, struct
main = open(sys.argv[1], 'rb').read()
L = lambda b, o: struct.unpack_from('>I', b, o)[0]
W = lambda b, o: struct.unpack_from('>H', b, o)[0]
# arcade records: course table 0x385d6, 29 longs
recs = {}
for i in range(29):
    r = L(main, 0x385d6 + i * 4)
    recs.setdefault(L(main, r), (i, r))
fields = {'trig+10': 0x10, 'ai+20': 0x20, 'obj+2a': 0x2a, 'def+8': 8, 'tbl+c': 0xc}
d = sys.argv[2]
for f in sorted(os.listdir(d)):
    if not (f.startswith('CRS_') or f.startswith('ADV_')): continue
    b = open(os.path.join(d, f), 'rb').read()
    subs = [0] if f.startswith('ADV_') else []
    if f.startswith('CRS_'):
        o = 0
        while True:
            v = L(b, o)
            if v >= len(b) or (subs and v <= subs[-1]): break
            subs.append(v); o += 4
    for s in subs:
        hdr = [W(b, s + k) for k in range(0, 0x18, 2)]
        pts = b[s + 0x18:s + 0x18 + 24]
        circ = next((c for c in recs if main[c:c + 24] == pts), None)
        line = '%s +%x hdr %s' % (f, s, ' '.join('%04x' % h for h in hdr))
        if circ is None:
            print(line, 'circuit ?'); continue
        i, r = recs[circ]
        hits = []
        for k, fo in fields.items():
            p = L(main, r + fo) if fo != 0x2a else L(main, r + 0x2a)
            if not (0 < p < 0x80000): hits.append('%s=bad' % k); continue
            pat = main[p:p + 16]
            j = b.find(pat, s, s + 0x8000)
            hits.append('%s:%x->%s' % (k, p, ('+%x' % (j - s)) if j >= 0 else '-'))
        print(line, 'arc entry %d rec %x circ %x |' % (i, r, circ), ' '.join(hits))
