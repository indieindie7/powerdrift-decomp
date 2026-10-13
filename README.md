# Power Drift (Sega, 1988) reverse-engineering notes and symbols

Hand-named function maps, Ghidra scripts and working notes for the arcade game **Power Drift**
(Sega Y-Board). The board runs three 68000 programs: `main` (game logic, course loading, car physics, AI),
`suby` (road/rotation layer, palette, attract mode, ranking and name entry) and `subx` (sprite list builder,
backup RAM, ROM/RAM test). Same method as [cybersled-decomp](https://github.com/indieindie7/cybersled-decomp)
and [scorcher-decomp](https://github.com/indieindie7/scorcher-decomp). Non-commercial, done for study and preservation.

All 721 functions are hand-named (main 199, suby 497, subx 25): no `FUN_` and no provisional names left.

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
