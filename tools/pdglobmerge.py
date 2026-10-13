"""pdglobmerge.py <ghidra dir>: merge globs_<cpu>.txt into glist_shared.txt (users prefixed by CPU) and glist_work_<cpu>.txt."""
import sys, re, collections, os
d = sys.argv[1]
sh = collections.defaultdict(list); refs = collections.Counter()
for cpu in ('main', 'subx', 'suby'):
    work = []
    for l in open(os.path.join(d, 'globs_%s.txt' % cpu)):
        m = re.match(r'0x([0-9a-f]{8}) refs (\d+) fns \d+: ?(.*)', l.strip())
        v = int(m.group(1), 16)
        if v < 0x0d0000:
            refs[v] += int(m.group(2)); sh[v].append('%s: %s' % (cpu, m.group(3)))
        else:
            work.append(l)
    open(os.path.join(d, 'glist_work_%s.txt' % cpu), 'w').writelines(work)
with open(os.path.join(d, 'glist_shared.txt'), 'w') as o:
    for v in sorted(sh):
        o.write('0x%06x refs %d | %s\n' % (v, refs[v], ' | '.join(sh[v])))
print('shared', len(sh))
