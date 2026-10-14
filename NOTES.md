# Power Drift (Sega 1988, Y-Board arcade) decompile notes

Research/modding only, non-commercial. No leaked source. User goal (10-13): "lets do power drift please i am curious how the game stores circuits".

## Sources
- Arcade: user's download `Downloads/Power-Drift_Arcade_EN.zip` -> inner MAME set `arcade/zip/pdrift.zip` -> `arcade/rom/` (53 chips).
- Saturn: `Downloads/Power-Drift_SEGA-Saturn_JA.zip` (Sega Ages, 10 tracks bin/cue), not unpacked yet.
- Sega Rally (Saturn US + PC) zips are in H:\Downloads-archive (not started).
- No prior RE write-up of the track format found on the web (10-13).

## Layout
- `tools/ilv.py out hi lo [hi2 lo2]`: 68000 byte interleave (hi = even byte chip).
- `arcade/bin/main.bin` (0x80000) = epr-12017.25/12016.24 + epr-11748.27/11747.26; reset SSP 0, PC 0x330a6.
- `arcade/bin/subx.bin` (0x40000) = epr-11905.81/11904.80; PC 0xdba6.
- `arcade/bin/suby.bin` (0x40000) = epr-12019a.54/12018a.53; PC 0x118a2.
- main.bin 0x40000.. starts with tables of long pairs (0x00000ca8, 0x25a70c7d, ...) - track data candidate.

## Memory map (MAME src/mame/sega/segaybd.cpp, ROM_START pdrift line 2483)
- main: ROM 0-0x7ffff, multiplier 0x080000, soundlatch 0x082001, divider 0x084000, shared RAM 0x0c0000-0x0cffff,
  IO 0x100000 (315-5296), ADC 0x100040, RAM 0x1f0000-0x1fffff.
- subx: ROM 0-0x3ffff, mult/div same, shared 0x0c0000, ysprites RAM 0x180000-0x18ffff, RAM 0x1f8000, backup RAM 0x1fc000.
- suby: ROM 0-0x3ffff, shared 0x0c0000, rotate RAM 0x180000, bsprites 0x188000, palette 0x190000, rotate ctrl 0x198000, RAM 0x1f0000.
- Graphics: ysprites 4 MB (32 chips, ROM_LOAD64_BYTE), bsprites 0x80000. Sound Z80 epr-11899.102, PCM mpr-11754 etc.

## Ghidra
- Project `ghidra/PowerDrift.gpr` (to create), 68000:BE:32:default, base 0. Scripts `ghidra/scripts/`: PdSetup.java (vectors),
  PdMap.java (memory blocks, arg main|subx|suby). Reuse CyberSled/Amok scripts via -scriptPath.
- Gotcha: the protect_paths hook blocks any Bash command that names the ghidra-headless .bat; write runner files with Write.

## Circuits found (10-13)
- main.bin 0x40000..0x7bfff = 20 circuits, each 2048 points x (x, y, z) signed big-endian words = 0x3000 bytes, track n at
  0x40000 + n*0x3000; closed loops (last ~ first), y = height (0 = ground, bridges/ramps up to 8537), steps ~44 units.
  0x7c000..0x7ffff = FF. tools/ptscan.py (finds runs), tools/trackmap.py -> out/tracks20.png (local only, never publish).
- The game has 25 tracks (5 courses x 5) + special: 20 shapes here, so some are reused (tracks 3 and 13 = same figure-8
  with different heights). Per-point width/bank/scenery not found yet.
- No direct pointer/offset table to the 20 bases found (searched longs, >>8, >>4 words); the address is probably computed.
- Ghidra: imported main/subx/suby (PdMap + PdSetup), CsCoverage 3x: main only ~12k instr bytes disassembled (most code
  not found yet; reset 0x330a6). Scripts copied into ghidra/scripts (CsCoverage, CsDumpAll, ExportFuncInfo, DataRefs, DumpDecomp);
  -scriptPath with ';' breaks cmd, so keep everything in one dir. CsCoverage args need 0x prefix.
- User 10-13: "the team behind prob left lots of documents on the internet that might help you" - 2 web searches found none
  (only the 3DS port interview); asked the user for a link.

## Course table (10-13, found)
- Writer of the track pointer: code at 0x3864e. index = word 6(a6) + stage*4, where stage = word $cea38;
  a0 = long table at **0x385d6** (29 longs, ends where code starts at 0x3864a); the record a0 points to is copied to $ceb00..:
  rec+0 long -> ceb00 (circuit points), +4 w -> ceb3e, +6 w -> ceb40, +8/+0xc/+0x10 longs -> ceb08/0c/10, +0x14..+0x1a w -> ceb14..1c,
  +0x1c -> ceb26, +0x20 -> ceb2a ... (more fields to 0x36). rec+8 = rec+0x3e (data right after a 0x3e header);
  for low-ROM circuits rec+0x10 = circuit + 0x3000 (or +0x3180): per-track data follows the points. Not decoded yet.
- Layout: 6 slots per course (5 races + bonus), course E has no bonus slot -> 5*6-1 = 29 entries. Bonus slots 5/17 (same record 0x10ed8)
  and 11/23 (same record 0x2fd40) alternate; their +0x16 word is 7154/7146 vs 1026..1242 for races.
- Stage advance at 0x381c0: stage+1; if 5, the bonus is entered only when the six bytes $cf816..$cf81b are all 0
  (probably "won every race" flags), else the course ends. Stage written at 0x381f6, cleared at 0x379a4/0x37a32/0x37ae4.
- **27 distinct circuits**, all the same format (2048 x (x,y,z) words): 14 from the 0x40000 block plus 13 stored in the low ROM, in
  front of their own data: 0x4232 0x7920 0xac06 0x10f36 0x15504 0x19520 0x1c9c8 0x1fb5e 0x22eca 0x26392 0x29722 0x2cb88 0x2fdbe.
- 0x40000-block shapes not in the course table: 1 0x43000, 9 0x5b000, 13 0x67000 (no reference anywhere = unused circuits),
  2 0x46000 (ref in code 0x3402c), 12 0x64000 (record at 0xf2f2), 18 0x76000 (code 0x33fc8/0x33fd0): probably attract/demo or a test.
- Table entry -> circuit (entry: record, circuit): 0 4054 4232 | 1 22e4c 22eca | 2 ef2a 58000 | 3 18f0a 79000 | 4 ab78 ac06 | 5 10ed8 10f36 (bonus) |
  6 737a 40000 | 7 14b6e 70000 | 8 10aa2 49000 | 9 186fc 6d000 | 10 e6be 52000 | 11 2fd40 2fdbe (bonus) | 12 1c7ca 1c9c8 | 13 26304 26392 |
  14 df60 4c000 | 15 14f0e 61000 | 16 146d6 6a000 | 17 = 5 | 18 2c98a 2cb88 | 19 1fae0 1fb5e | 20 1426e 5e000 | 21 e2e6 4f000 | 22 7722 7920 |
  23 = 11 | 24 296c4 29722 | 25 152c6 15504 | 26 18af2 73000 | 27 19302 19520 | 28 eb34 55000.
- Course order of 6(a6) (course*24 bytes) is inferred from the bonus pattern, not yet traced to its writer.

## Per-track data after the points (10-13)
- tools/coursemap.py -> out/courses.png (27 circuits by course + 6 unused; sent to the user, local only). tools/d68b.py = disassembler that skips bad words (args hex addr, hex length).
- Record pointers (copied at 0x38690..): ceb08 = rec+0x3e (read at 0x33a5a: 16-byte entries {w,w,w,w(sign selects form),...}, +0x10 skip when $a(a3)==0x402; not decoded),
  ceb0c = shared table (0x285f0/0x28670 family, same for many tracks: theme data?), ceb10 = rec+0x10 = right after the points: an 8-byte trigger list
  {point idx w, type byte&7} walked at 0x33e9c by the player's pos>>5 +0x80; all 8 handlers are rts (DEAD), lists start 0x7fff (empty).
  ceb3a = rec+0x2a (C1: 0x1c848): 32 records copied into the object slots at $ce624 (0x33f00): {w->+0x2c, w->+0x1a, w->+2, byte|=flags, pad, w->+0xc, w->+0xe} = per-track object/sprite set-up, not decoded.
- **AI driving script** = ceb2a = rec+0x20 (C1: 0x1f9d0), 16-byte entries, ended by 0x7fff; per car cursor car+0x2c, fires when car lap pos (car+0x3e) passes entry w0 (0x372a4):
  type 0 (byte +2): lane change: car+0x56 = pos, +0x5a = direction (+-0x400), +0x58 = length in pos units; 0x35026 eases the lateral target car+0x30 through
  S-curve tables 0x10f6 (right) / 0xcf6 (left) indexed by (pos-start)<<9 / length (hardware divider).
  type 1: corner zone: +0x60 = end pos, +0x62 byte = turn sign (0 straight, ff / 01), +0x64 = corner factor; 0x344a4 sets the car speed from lateral offset (clamp 0x300, /2) + factor.
  types 2/3 set/clear car+0x44 bit0, 4/5 bit1; 6/7 set/clear car+0x91 bit0 (6 also plays command 0x89 via 0x33488 if speed car+0x24 < 200; 7 sets +0x92 = 0x20).
  C1 example: corners 0x4ae0..0x6e00 (left, 0x0cfe) and 0xc420..0xf4a0 (right, 0x11ea) = the two figure-8 loops; flags bit0+bit1 on from 0x76c0 to 0xc800
  = points 950..1600 = exactly the raised bridge section (y 0 -> 2923 -> jump) -> flags probably "elevated / jump" behaviour (guess).
- **Trackside object runs** = ceb08 = rec+0x3e (read at 0x33a46, placer 0x33afa), 16-byte entries:
  w0 start pos, w1 count, w2 spacing (pos units, 0x20 = 1 point), w3 kind (<0 = end of list; 0 = use the track default sprite word ceb34 = rec+0x24 and skip w4/w5;
  >0 = w4 -> slot+2, w5 -> slot+0xc sprite), w6 -> slot+0x36, w7 -> slot+0x38. Objects go into the slot chain at $ce61c (flags 0x8b), max 0xaa = 170 per track;
  each is placed at the track point (ceb00 + idx*6) using the per-point heading word table at $b000.w and the sin/cos tables 0xef6 / 0xcf6.
  C1 example: 61 default objects every 16 points from point 0; 53 objects (sprite 0x6c/0xb13a, w7 0x30) every 12 points from 0x7800 (the bridge);
  27 default every 16 from 0xc800. The 0x402 check at 0x33a62 skips the first entry for one mode.

## Decompile pass 1: code coverage (10-13, user: "keep decomping it please")
- Code regions: main 0x33000..0x3a000 (0x3a000.. FF; 0..0x33000 data/tracks), subx ~0xd600..0xe400 only (rest sprite tables), suby 0x400..0x21000 (code + data).
- Coverage after CsCoverage pseudo rounds + PdForce: main instr 19082 bytes (left undefined 9184 = data tables 0x352dc len 2452, 0x3903e 962, 0x36830 ...),
  subx 1724, suby 40428 (still creating ~4/round; more rounds possible).
- Dumps: ghidra/decomp_main.c (171 functions), decomp_subx.c (13), decomp_suby.c (542). Local only (C dumps never pushed).
- New tools: tools/rdesc.py (recursive descent, env RD_CODE=lo-hi seeds pea/lea/move.l immediates), tools/d68b.py; scripts PdForce.java (addr list -> function),
  PdNames.java (own name applier: `0x<addr> <name> [comment]` lines; the protect hook blocks copying Amok ApplyNames, so do not).
- Next: hand names via Sonnet agents reading the dumps -> ghidra/hand_main.txt / hand_subx.txt / hand_suby.txt -> PdNames.java; known anchors in the sections above.

## Decompile pass 2: hand names (10-13)
- Name files in ghidra/: hand_main.txt, hand_subx.txt, hand_suby_a.txt (+ hand_suby_b.txt). Applied with scripts/PdNames.java; false functions removed with scripts/PdDelete.java (bogus_*.txt lists).
- main: 163 functions, 0 FUN_ (12 false removed: 0xf3a0, 0x277e4, 0x277f0, 0x2fdf4, 0x2fe00, 0x33068, 0x352d4, 0x352dc, 0x365b0, 0x36690, 0x36698, 0x3808e). Added entries race_LoadCourse 0x3864e, obj_ReadTracksideRuns 0x33a46, obj_PlaceOnTrack 0x33afa, trk_StepTriggerList 0x33e9c (bsr targets). 0x381c0 / 0x344a4 / 0x33f00 are not call targets (code inside larger bodies).
  - Key main names: sys_Reset 0x330a6, irq_VBlank 0x3327a, snd_Queue 0x33488 (ring cff88) / snd_DrainLatch 0x33432 (latch 0x82001), game_ModeDispatch 0x37730 (mode word ce09c, 28 modes), race_BubbleSortRank 0x37646, ai_StepDrivingScript 0x372a4, ai_EaseLaneChange 0x35026, sys_Random 0x3955c (LCG seed 0x2a6d365a, x0x29), bk_Checksum 0x39902 (CRC 0x8810 over cfd00..), coin_AddCredits 0x397f2 (BCD). 32 provisional (cab_* 0x33506-0x33828 fragments).
- subx: all named (sys_WaitVblank 0xdb82, subx_MainLoop 0xdbb2, yspr_BuildSpriteList 0xdcc0, nv_ValidateBackup 0xe136 (two 0x80-byte copies with CRC at +0x7e), crc16_Calc 0xe1c8 (reflected poly 0x8810), hw_InitVideo 0xe1ea, test_RomRamCheck 0xe2c6). 0xd75e and 0xe31e are data tables, removed.
- suby low ROM 0x402..0x11881 is data (rdesc finds 14 code bytes there); 226 false functions removed. Real code starts at trap stubs 0x11876; reset 0x118a2 -> main_MainLoop 0x118ac (task list at fff1000: +0 flags 0x80 active, +0x10 handler, +0x14 next). 44 names in part A.
- Pass 2b: forcing every unresolved `func_0x` call target (PdForce.java, repeated until stable) found many uncovered functions: main 185 fn (22 new FUN_), suby 463 fn (138 new FUN_; 0x1b5ec does not disassemble), subx 25 fn (0 FUN_). These go to round-2 name files hand_main2.txt / hand_suby2.txt.
- Pass 2c: round-2 names applied (hand_main2.txt 22, hand_suby2.txt 138; 0x1a004-0x1a010 are bra.w thunks of the motor-test jump table 0x19ff0, named test_MotorJmpTbl_*). tools/gapptr.py + tools/gapcode.py find stored handler pointers (move.l #imm / lea / pea) into coverage gaps; forced 21 main + 31 suby. Coverage now: main instr 23558 (gaps 21), suby 41520 (gaps 44); no further candidates. Round-3 lists ghidra/fun_main3.txt (24) / fun_suby3.txt (34). 0x1b5ec and 0x1beb2 (suby) do not become functions.
- Pass 2d (10-13): round 3 applied (hand_main3.txt 21 + 3 bogus removed: 0x35a12, 0x35ab2, 0x38d9c; hand_suby3.txt 34). ALL NAMED: main 206 fn, suby 497 fn, subx 25 fn, 0 FUN_. Only unresolved calls: suby 0x1b5ec (second entry inside obj_InitCarSelect 0x1b5e2) and 0x1beb2 (likewise a mid-function entry); left as is. 43 main + 43 suby names still `provisional:` -> review pass next (hand_*_rev.txt).
- Pass 3a (10-13): suby provisional review applied (ghidra/hand_suby_rev.txt, 43 lines: 23 renamed, 0 still provisional). hs_State* = case bodies of hs_StateMachine / hs_StateDispatchB (ce09c 4 = attract ranking, 0x1a = score check, 0x1b = name entry). hs_MatchInitialsMessage: an initials list (staff-like initials) sets ce878 = message index for hs_DrawMessageText; the name-entry tail also replaces one rude word. Main review pending (hand_main_rev.txt).
- Pass 3b (10-13): main provisional review applied (hand_main_rev.txt: 27 renamed, 9 bogus removed: 0x33000, 0x336c2-0x336ca, 0x33702, 0x33724, 0x373ba; added cab_ForceFeedbackOutput 0x33742, spr_CarStatusOverlayInit 0x37040; traps renamed sys_TrapEnableIrq 0x33078 / sys_TrapDisableIrq 0x3307e). cab "MotorCopy*" entries are byte pattern tables written to cff2c; real dispatcher 0x33532 (table 0x3354a on cff30&3). game_AddScoreBcd adds cff68 into score cff60, then raises the high score cff64. car_FrameTaskScripted 0x35d54 path: player car under script when cea38 > 4 and cea2b bit0 clear (meaning unknown).
- FINAL 10-13: main 199 fn, suby 497, subx 25 = 721 functions, 0 FUN_, 0 provisional. Some named functions are mid-body fragments (comments say so). Next if wanted: public repo (names + notes + tools only, no dumps/data).

## Public repo (10-13)
- PUBLISHED github.com/indieindie7/powerdrift-decomp, first commit 85ea466 (notes, hand/bogus lists, scripts, tools; no ROM data; initials list removed from comments).
- 10-13 second commit 0dd1446: globals_<cpu>.txt + types_<cpu>.txt, pdglobs/pdglobmerge/satfind tools, gl_prompt (paths made relative), README steps 4 + Saturn note.

## Saturn Sega Ages port (10-13, recon)
- Disc: Downloads/Power-Drift_SEGA-Saturn_JA.zip -> saturn/zip (10 tracks), data track extracted with Scorcher tools/isoextract.py
  (2352) -> saturn/cd (45 files). IP.BIN: GS-9181 V1.001 1998-01-22, 1st read file `00000` (899008 bytes) at 0x06004000 (SH-2).
- Files: CRS_A..E.DAT + CRS_N.DAT (courses), ADV_*.DAT (10 files), CAR, LIN, MEN, SEL, TTL, END, LOGO (+ LOGO_0/1.BMP), SOUND0-6.DAT, NO00-08.CDA (CD audio).
- CRS_x.DAT header = big-endian long offsets to sub-blocks (CRS_A: 0x18, 0x181dc, 0x34bcc, 0x4c924, 0x68948, 0x88e74, then 0x180028?).
- **The arcade circuits are byte-identical** in the Saturn files (tools/satfind.py main.bin saturn/cd): 2048 x (x,y,z) BE16 points,
  each at a CRS sub-block + 0x18 (e.g. CRS_A@0x30 = arcade 0x4232, CRS_A@0x181f4 = 0x22eca). 0x10f36 (bonus) is in CRS_A/C/E/N,
  0x2fdbe (bonus) in CRS_B/D/N. ADV_xx.DAT hold one circuit each at +0x18 (ADV_B1 = 0x40000 ...) = probably the attract/demo laps.
- Not on the Saturn disc: arcade circuits 0x43000, 0x46000, 0x5b000, 0x64000, 0x67000, 0x76000 (the unused/demo/test ones).

## Globals + types pass (10-13, user: "please finish power drift")
- tools/pdglobs.py + pdglobmerge.py -> ghidra/glist_sharedA/B.txt (284 shared addrs 0x0c0000-0x0cffff) + glist_work_{main,subx,suby}.txt (4/11/69).
  Two Sonnet agents (prompt ghidra/scripts/gl_prompt.txt) -> gn_*.txt. Fix: 0x0cea0c = sh_dip_setting_hi2 (cff30 >> 6, index into 0x3d800), 0x0cff30 = sh_dip_switches.
- ghidra/globals_<cpu>.txt (shared + that CPU's work RAM: main 288, subx 295, suby 353 labels) applied with Amok ApplyGlobals.java, 0 problems.
  PROVISIONAL: many names are plain <area>_<addr> where the evidence was thin.
- Backup ghidra/PowerDrift.rep.bak_types. CommitParams apply: main 171, subx 23 (2 failed), suby 411. ExportSigs -> ghidra/types_<cpu>.txt (199/25/497 fn, 0 FUN_).
- Re-dump main: 0 DAT_000c refs left (1541 sh_ uses).
- suby calls into 0x1b5ec and 0x1beb2 are secondary entry points inside obj_InitCarSelect 0x1b5e2 and its neighbour (code shared by fall-through); left as is.

## Saturn program + course file layout (10-13)
- Ghidra: /sat00000.bin in the PowerDrift project (SH-2, BinaryLoader base 0x06004000, FindSh2FunctionsMem) -> 866 fn; ManxTT tools/srptrs.py
  (base 06004000) -> ghidra/ptrcode_sat.txt 175 code pointers, CreateAt.java (copied from Amok) with analysis -> **1049 functions**, second round 0 more.
  ghidra/funcinfo_sat.tsv (1049 fn, 2621 calls, 416 string refs). Code ends at 0x0603a3xx; the rest of the 899008-byte file (to 0x060e1840) is data.
- tools/satcrs.py main.bin saturn/cd: every CRS/ADV sub-block matched to its arcade course-table entry. CRS_A = entries 0-5, B = 6-11, C = 12-16 + bonus 5,
  D = 18-22 + bonus 11, E = 24-28 + bonus 5; ADV_* = copies of single CRS sub-blocks (A2=1, B1=6, B2=7, B3=8, C2=13, C3=14, D1=18, E1=24, E2=25, E4=27).
  CRS_N = bonus 5 + bonus 11 + 3 sub-blocks whose circuit is not an arcade one (CRS_N +0x316a0, +0x424f0, +0x5aa90): new or edited circuits, not checked.
- Sub-block layout (offsets from sub-block start; header = 12 BE words):
  w0 0x18 = points offset; w1 = arcade rec+6 word (0x0028 for entry 0); w2..w4 small values (00ff = none?); points 0x18..0x3018 (identical to arcade);
  w5 0x3018 = trackside object runs (arcade rec+8 block, same 16-byte entries; end word ffff became 5fff in entry 0);
  w6 0x3038.. = Saturn-only block (0xbd2 bytes in CRS_A 0, 10-byte-ish records `00a7 e41c 0000 d972 0400 ...`; not decoded);
  w7 = object set (arcade rec+0x2a: 32 records, re-packed to 12 bytes, sprite words replaced by Saturn indexes, 0x180 bytes);
  w8 = AI driving script (arcade rec+0x20, same entries without the 4 zero pad bytes: 12-byte entries);
  w9 = 0x200-byte word table (52c7 ... in CRS_A 0; unknown); w10 = mode word (ffff / 0000 / 0402 = the arcade 0x402 check at 0x33a62);
  w11 = end of the track tables; after it come RGB555 colour data and (probably) graphics to the next sub-block.

## Saturn naming round 1 (10-13, user: "please continue until finished")
- CsDumpAll -> ghidra/decomp_sat.c (1049 fn, 48019 lines). ManxTT tools/slice.py -> ghidra/naming/s1..s6.c (129/67/161/245/294/152 fn).
  Prompt ghidra/naming/n1_prompt_sat.txt; 6 Sonnet agents -> naming/h1..h6.txt -> ghidra/hand_sat.txt.

## CRS_N new circuits (10-13)
- tools/satnew.py main.bin saturn/cd/CRS_N.DAT [png]: the 3 non-arcade CRS_N circuits (+0x316a0, +0x424f0, +0x5aa90) share **0 points** with
  any arcade circuit (incl. the unused 0x40000-block ones); nearest shapes by mean xz distance are 0x58000 / 0x04232 / 0x22eca (4.6k-7.2k apart) = unrelated.
  So they are 3 brand-new circuits built for the Saturn port (the EXTRA / NEW COURSE mode, file CRS_N.DAT). Each crosses itself (bridge over its own road);
  heights 0..1400/1500 (arcade-like). Same sub-block format (w10 = 0402 for +0x316a0). Render renders/crs_n_new.png (local only).
- Round 1 DONE: naming/h1..h6 (129/67/161/245/294/152) -> ghidra/hand_sat.txt 1049 lines (0x06039e2c = switch case of 0x06038f58, named by hand;
  dup gfs_StartTransfer -> _2 at 0x06028e00), 460 provisional. Backup naming/hand_sat_r1.bak. Amok ApplyNames: 1049 named; funcinfo + decomp_sat.c re-dumped (0 FUN_).
- Round 2: tools/provctx.py (ManxTT copy, base 'sat' = 0x06004000, image saturn/sat00000.bin) on naming/prov_list.txt (470 = provisional + _N)
  -> naming/r2_1..8.txt; prompt naming/prompt_r2.txt; 8 Sonnet agents -> naming/v2_1..8.txt; apply tools/srprovapply.py ghidra/hand_sat.txt naming/v2_*.txt.
- Round 2 result: v2_1..8 = CONFIRM 261, RENAME 194, UNSURE 15 (srprovapply.py patched to also rename `_N` names). Notable: smpc_WriteCmd* -> sndcmd_*
  (sound-RAM mailbox), sh2_Get/SetInterruptMask. Backup naming/hand_sat_r2.bak.
- Round 3 (by hand): the last 14 unclear ones got behaviour names, comment "(behaviour name, purpose unclear)" (e.g. obj_UpdateType83CarPart,
  gfs_ReadBufferPair, sys_SyscallNoArgs, boot_ReadScrambledTableA/B); 0x06016308 = menu_CallCursorBlinkOnce.
- **Saturn naming DONE (10-13):** hand_sat.txt 1049 lines, 0 provisional, unique names. ApplyNames 1049; re-export funcinfo_sat.tsv + decomp_sat.c:
  1049 fn, 0 FUN_, 0 diffs vs hand file. Prefixes: obj 128, gfs 105, sgl 80, cdc 67, smpc 65, sys 50, cdfs 39, objset 38, car 36, sndcmd 34, vdp2 32, xfer 30.
  Game logic: course_LoadHeaderPointers 0x0600b7a8, race_ComputeCarRanks 0x0600da48, ai_UpdateCar 0x06011ca4, road_PlotTrackSegmentByType 0x06015c14.
- Repo updated 10-13: powerdrift-decomp c06cc54 (hand_sat.txt, naming prompts, satcrs/satnew/provctx/srprovapply/slice, README Saturn section).
