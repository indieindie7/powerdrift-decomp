"""ilv.py - interleave 68000 even/odd byte ROMs: ilv.py out hi lo [hi2 lo2 ...] (hi = even bytes)."""
import sys
out, files = sys.argv[1], sys.argv[2:]
data = bytearray()
for i in range(0, len(files), 2):
    a, b = open(files[i], 'rb').read(), open(files[i + 1], 'rb').read()
    for x, y in zip(a, b):
        data += bytes((x, y))
open(out, 'wb').write(data)
print(out, hex(len(data)))
