// PdMap.java: Sega Y-Board memory blocks (MAME segaybd.cpp). Arg: main | subx | suby.
//@category PowerDrift
import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.*;
public class PdMap extends GhidraScript {
  void blk(String n, long a, long len, boolean vol) throws Exception {
    Memory m = currentProgram.getMemory();
    if (m.getBlock(toAddr(a)) != null) return;
    MemoryBlock b = m.createUninitializedBlock(n, toAddr(a), len, false);
    b.setRead(true); b.setWrite(true); b.setVolatile(vol);
    println(String.format("%s %06x +%x", n, a, len));
  }
  public void run() throws Exception {
    String cpu = getScriptArgs().length > 0 ? getScriptArgs()[0] : "main";
    blk("MULT", 0x080000, 0x2000, true);
    blk("DIVIDER", 0x084000, 0x2000, true);
    blk("SHARERAM", 0x0c0000, 0x10000, false);
    if (cpu.equals("main")) {
      blk("SOUNDLATCH", 0x082000, 0x2000, true);
      blk("IO", 0x100000, 0x40, true);
      blk("ADC", 0x100040, 0x8, true);
      blk("RAM", 0x1f0000, 0x10000, false);
    } else if (cpu.equals("subx")) {
      blk("YSPRITES", 0x180000, 0x10000, false);
      blk("RAM", 0x1f8000, 0x4000, false);
      blk("BACKUPRAM", 0x1fc000, 0x4000, false);
    } else {
      blk("ROTATERAM", 0x180000, 0x8000, false);
      blk("BSPRITES", 0x188000, 0x8000, false);
      blk("PALETTE", 0x190000, 0x8000, false);
      blk("ROTCTRL", 0x198000, 0x8000, true);
      blk("RAM", 0x1f0000, 0x10000, false);
    }
  }
}
