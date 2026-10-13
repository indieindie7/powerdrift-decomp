"""satfind.py <main.bin> <saturn cd dir>: look for each arcade circuit (first 24 bytes of its points) in the Saturn files,
also as little-endian / 32-bit forms; prints file + offset of hits."""
import sys, os, struct
main = open(sys.argv[1], 'rb').read()
bases = [0x40000 + i * 0x3000 for i in range(20)] + [0x4232, 0x7920, 0xac06, 0x10f36, 0x15504, 0x19520, 0x1c9c8,
                                                     0x1fb5e, 0x22eca, 0x26392, 0x29722, 0x2cb88, 0x2fdbe]
files = {f: open(os.path.join(sys.argv[2], f), 'rb').read() for f in os.listdir(sys.argv[2])}
for b in bases:
    w = struct.unpack('>12h', main[b:b + 24])
    pats = {'be16': main[b:b + 24], 'le16': struct.pack('<12h', *w), 'be32': struct.pack('>12i', *w),
            'be32fx': struct.pack('>12i', *[v << 16 for v in w])}
    hits = []
    for f, d in files.items():
        for k, p in pats.items():
            i = d.find(p)
            if i >= 0: hits.append('%s@%x(%s)' % (f, i, k))
    print(hex(b), w[:3], hits or '-')
