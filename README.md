# Power Drift (Sega, 1988) reverse-engineering notes and symbols

Hand-named function maps, Ghidra scripts and working notes for the arcade game **Power Drift**
(Sega Y-Board). The board runs three 68000 programs: `main` (game logic, course loading, car physics, AI),
`suby` (road/rotation layer, palette, attract mode, ranking and name entry) and `subx` (sprite list builder,
backup RAM, ROM/RAM test). Same method as [cybersled-decomp](https://github.com/indieindie7/cybersled-decomp)
and [scorcher-decomp](https://github.com/indieindie7/scorcher-decomp). Non-commercial, done for study and preservation.

All 721 arcade functions are hand-named (main 199, suby 497, subx 25), and all 1049 functions of the Saturn port: no `FUN_` and no provisional names left.

## How the game stores circuits

Each circuit is 2048 points of signed big-endian `(x, y, z)` 16-bit words (0x3000 bytes), a closed loop.
The course table at main `0x385d6` has 29 entries for 27 distinct circuits. After the points come the
per-track blocks: the AI driving script, trackside object runs and the trigger list. `NOTES.md` sections
"Circuits found", "Course table" and "Per-track data after the points" have the layouts and the code that reads them
(`race_LoadCourse` 0x3864e, `obj_ReadTracksideRuns` 0x33a46, `ai_StepDrivingScript` 0x372a4, `trk_StepTriggerList` 0x33e9c).

## What is here

| Path | Content |
|---|---|
| `NOTES.md` | the full working log: ROM layout, memory map, circuit format, coverage passes, every naming round |
| `ghidra/hand_<cpu>*.txt` | hand-named functions (`0x<addr> <name> [comment]`), applied in file order; `_rev` files are the final review |
| `ghidra/globals_<cpu>.txt` | RAM labels: shared RAM `sh_` (0x0c0000, seen by all three CPUs) + that CPU's work RAM `g_`; **provisional**, many names are plain area names |
| `ghidra/types_<cpu>.txt` | committed function signatures (from the decompiler) |
| `ghidra/bogus_<cpu>*.txt` | false function starts that were deleted (data decoded as code) |
| `ghidra/scripts/` | headless Ghidra scripts: memory map and vectors (`PdMap`, `PdSetup`), names (`PdNames`), deletions (`PdDelete`), forced code starts (`PdForce`), coverage, pointer scan, data refs, decompile dump |
| `ghidra/pdrun.sh` | headless runner (set `GHIDRA_HEADLESS` and `PD_GHIDRA`) |
| `tools/ilv.py` | joins the even/odd byte ROM chips into one program image |
| `tools/rdesc.py`, `d68b.py`, `gapptr.py`, `gapcode.py` | recursive-descent code finder and gap scanners for code reached only through stored pointers (needs `capstone`) |
| `tools/coursemap.py` | draws every circuit from your own `main.bin` (local viewing only) |

## What is NOT here

No game files: no ROMs, no interleaved program images, no data dumps, no circuit renders, no decompiled C
output and no Ghidra project database (which embeds the binaries). You need your own copy of the MAME set `pdrift`.

## Reproducing the Ghidra project

1. Interleave the program chips with `tools/ilv.py` into `main.bin` (0x80000), `subx.bin` and `suby.bin`
   (0x40000 each); the chip list is in `NOTES.md` "Layout".
2. Ghidra 12.1.4: import each as 68000:BE:32:default at base 0, run `PdSetup.java` (vectors) and
   `PdMap.java main|subx|suby` (memory map from MAME `segaybd.cpp`).
3. Per program, run `PdDelete.java` with the `bogus_` lists and `PdNames.java` with each `hand_` file in this
   order: `hand_<cpu>.txt`, `2`, `3`, `_a`, `_b`, then `_rev` last (later files rename earlier entries).
4. Apply `globals_<cpu>.txt` with amok-decomp's `ApplyGlobals.java`, then its `CommitParams.java apply`.

## Saturn Sega Ages port (1998)

The main program (CD file `00000`, SH-2, loaded at 0x06004000) is fully hand-named too: **1049 functions**,
no `FUN_` and no provisional names (`ghidra/hand_sat.txt`, same line format; apply with amok-decomp's `ApplyNames.java`).
Biggest groups: game objects `obj`/`objset`, the CD file layer `gfs`/`cdc`/`cdfs`, Sega SGL graphics `sgl`, SMPC/peripherals,
the sound-RAM command mailbox `sndcmd`, cars `car`, AI `ai`, road drawing `road`.

How the Saturn stores circuits: the arcade circuits sit in the program image byte for byte (`tools/satfind.py`), and the
course files `CRS_A..E.DAT` / `CRS_N.DAT` hold sub-blocks of a 12-word header, the same 2048 `(x, y, z)` points, then the
trackside runs, object set, AI script and colour data (`NOTES.md` "Saturn program + course file layout", `tools/satcrs.py`).

`CRS_N.DAT` (EXTRA / NEW COURSE) holds **3 circuits that are not in the arcade game at all**: they share no point with any
arcade circuit, and each one crosses over itself. `tools/satnew.py` compares them with every arcade circuit
(`NOTES.md` "CRS_N new circuits").

Naming method: Ghidra decompile split into slices (`tools/slice.py`), one Sonnet agent per slice with
`ghidra/naming/n1_prompt_sat.txt`, then a review round over every provisional name with context from `tools/provctx.py`
and `ghidra/naming/prompt_r2.txt` (applied by `tools/srprovapply.py`), then the last 14 by hand.
