"""rdesc.py <bin> <romsize hex> [extra hex entries...]: recursive-descent 68000 code finder.
Seeds: reset PC + vectors 2..47 (and 0x60..0x7c autovectors) + extra args. Follows bra/bcc/dbcc/jmp/jsr/bsr with
absolute or PC-relative targets, `jmp/jsr (d,pc,dn)` bra.w tables, stops at rts/rte/rtr/jmp(an)/illegal.
Prints 'F <addr>' for call targets/seeds and 'C <lo> <hi>' covered runs; summary to stderr."""
import sys, struct, re, os, capstone
CODE = tuple(int(x, 16) for x in os.environ['RD_CODE'].split('-')) if os.environ.get('RD_CODE') else None
b = open(sys.argv[1], 'rb').read()
rom = int(sys.argv[2], 16)
md = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
md.detail = False
L = lambda a: struct.unpack_from('>I', b, a)[0]
funcs, seen, work = set(), {}, []
def seed(a, f=True):
    if 0x400 <= a < rom and a % 2 == 0:
        if f: funcs.add(a)
        work.append(a)
seed(L(4))
for v in list(range(2, 48)):
    t = L(v * 4)
    if t not in (0, 0xffffffff): seed(t)
for x in sys.argv[3:]: seed(int(x, 16))
def target(op):
    op = op.strip()
    if op.endswith('(pc)'): op = op[:-4]
    if op.startswith('$') and ',' not in op and '(' not in op:
        return int(op[1:].split('.')[0], 16)
    return None
while work:
    a = work.pop()
    while 0 <= a < rom and a not in seen:
        i = next(md.disasm(b[a:a + 10], a), None)
        if i is None: break
        seen[a] = i.size
        m, op = i.mnemonic, i.op_str
        nxt = a + i.size
        if m in ('rts', 'rte', 'rtr', 'illegal'): break
        if m.startswith(('bra', 'jmp')):
            t = target(op)
            if t is not None: seed(t, False)
            elif '(pc, d' in op:   # jmp/jsr table of bra.w following the next instruction
                p = nxt
                while p < rom and struct.unpack_from('>H', b, p)[0] == 0x6000:
                    seed(p + 2 + struct.unpack_from('>h', b, p + 2)[0], False); p += 4
            break
        if m.startswith(('jsr', 'bsr')):
            t = target(op)
            if t is not None: seed(t)
            elif '(pc, d' in op:
                p = nxt
                while p < rom and struct.unpack_from('>H', b, p)[0] == 0x6000:
                    seed(p + 2 + struct.unpack_from('>h', b, p + 2)[0], True); p += 4
        elif m.startswith(('b', 'db')) and m.split('.')[0] not in ('bchg', 'bclr', 'bset', 'btst'):
            t = target(op.split(',')[-1])
            if t is not None: seed(t, False)
        if CODE:
            for mm in re.finditer(r'[#]?[$]([0-9a-f]+)', op if m.startswith(('pea', 'lea', 'move.l')) else ''):
                v = int(mm.group(1), 16)
                if CODE[0] <= v < CODE[1] and v % 2 == 0 and v not in seen: seed(v)
        a = nxt
runs, lo, prev = [], None, None
for a in sorted(seen):
    if lo is None: lo = a
    elif a != prev: runs.append((lo, prev)); lo = a
    prev = a + seen[a]
if lo is not None: runs.append((lo, prev))
for f in sorted(funcs): print('F %x' % f)
for r in runs: print('C %x %x' % r)
print('funcs %d, instr bytes %d, runs %d' % (len(funcs), sum(seen.values()), len(runs)), file=sys.stderr)
