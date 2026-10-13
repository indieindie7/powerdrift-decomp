"""gapcode.py <bin> <coverage log>: candidates from gapptr whose referencing instruction is a code-pointer store
(move.l #imm,... / lea abs / pea abs) and whose target decodes as valid 68000 code up to a terminator."""
import sys, re, struct, capstone
b = open(sys.argv[1], 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
gaps = [(int(m.group(1), 16), int(m.group(2))) for m in re.finditer(r'gap ([0-9a-f]+) len (\d+)', open(sys.argv[2]).read())]
ingap = lambda a: any(lo <= a < lo + n for lo, n in gaps)
def valid(a):
    for k in range(60):
        i = next(md.disasm(b[a:a + 10], a), None)
        if i is None: return False
        if i.mnemonic in ('rts', 'rte', 'jmp') or i.mnemonic.startswith('bra'): return True
        a += i.size
    return True
out = set()
for i in range(2, len(b) - 3, 2):
    v = struct.unpack_from('>I', b, i)[0]
    if v >= len(b) or v % 2 or not ingap(v): continue
    op = struct.unpack_from('>H', b, i - 2)[0]
    store = (op & 0xf03f) == 0x203c or op in (0x4879,) or (op & 0xf1ff) == 0x41f9   # move.l #imm,<ea> / pea / lea abs.l
    if store and valid(v): out.add(v)
print(' '.join('0x%x' % v for v in sorted(out)))
