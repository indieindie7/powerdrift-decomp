"""d68b.py <bin> <hexaddr> <hexbytes>: 68000 disassembly that steps over undecodable words (dc.w)."""
import sys, capstone
b = open(sys.argv[1], 'rb').read()
a, end = int(sys.argv[2], 16), int(sys.argv[2], 16) + int(sys.argv[3], 16)
md = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
while a < end:
    i = next(md.disasm(b[a:a + 10], a), None)
    if i is None: print('%06x  dc.w     $%s' % (a, b[a:a+2].hex())); a += 2; continue
    print('%06x  %-8s %s' % (i.address, i.mnemonic, i.op_str)); a += i.size
