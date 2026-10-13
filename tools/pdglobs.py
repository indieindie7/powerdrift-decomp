"""pdglobs.py <decomp.c> <out>: DAT_ refs to shared RAM 0x0c0000-0x0cffff and work RAM (0xffff0000.., 0x1f0000..)
with ref count and the user functions (input for the globals naming pass)."""
import sys, re, collections
cnt = collections.Counter(); users = collections.defaultdict(set); fn = None
for l in open(sys.argv[1], encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    for a in re.findall(r'DAT_([0-9a-f]{8})\b', l):
        v = int(a, 16)
        if 0x0c0000 <= v < 0x0d0000 or v >= 0xffff0000 or 0x1f0000 <= v < 0x200000:
            cnt[v] += 1; users[v].add(fn)
with open(sys.argv[2], 'w') as o:
    for v in sorted(cnt):
        u = sorted(users[v])
        o.write('0x%08x refs %d fns %d: %s\n' % (v, cnt[v], len(u), ' '.join(u[:8])))
print(len(cnt), 'shared', sum(1 for v in cnt if v < 0x0d0000), 'work', sum(1 for v in cnt if v >= 0x0d0000))
