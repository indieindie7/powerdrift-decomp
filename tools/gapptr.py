"""gapptr.py <bin> <coverage log>: for each CsCoverage gap, list even addresses inside it that appear as a
32-bit big-endian value somewhere in the binary (stored handler pointers the call-graph walk missed)."""
import sys, re, struct
b = open(sys.argv[1], 'rb').read()
gaps = [(int(m.group(1), 16), int(m.group(2))) for m in re.finditer(r'gap ([0-9a-f]+) len (\d+)', open(sys.argv[2]).read())]
refs = {}
for i in range(0, len(b) - 3, 2):
    v = struct.unpack_from('>I', b, i)[0]
    if v < len(b): refs.setdefault(v, []).append(i)
for lo, n in gaps:
    for a in range(lo, lo + n, 2):
        if a in refs: print('%x in gap %x: refs %s' % (a, lo, ' '.join('%x' % r for r in refs[a][:4])))
