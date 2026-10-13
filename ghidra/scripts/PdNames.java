// PdNames.java <names.txt>: apply hand names. Line format: `0x<addr> <name> [comment...]` (# = comment line).
// Creates the function if missing (disassembling first), renames it USER_DEFINED, puts the comment as the plate comment.
//@category PowerDrift
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import java.nio.file.*;
public class PdNames extends GhidraScript {
  public void run() throws Exception {
    int ok = 0, bad = 0;
    for (String ln : Files.readAllLines(Paths.get(getScriptArgs()[0]))) {
      ln = ln.trim();
      if (ln.isEmpty() || ln.startsWith("#")) continue;
      String[] p = ln.split("\\s+", 3);
      Address a = toAddr(Long.decode(p[0]));
      Function f = getFunctionAt(a);
      if (f == null) {
        new DisassembleCommand(a, null, true).applyTo(currentProgram, monitor);
        if (getInstructionAt(a) != null) f = createFunction(a, null);
      }
      if (f == null) { println("FAIL " + p[0] + " " + p[1]); bad++; continue; }
      f.setName(p[1], SourceType.USER_DEFINED);
      if (p.length > 2) f.setComment(p[2]);
      ok++;
    }
    println("PdNames applied " + ok + ", failed " + bad);
  }
}
