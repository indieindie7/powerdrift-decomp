// PdForce.java <hexaddr...>: disassemble at each address and create a function there (code the gap finders missed).
//@category PowerDrift
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
public class PdForce extends GhidraScript {
  public void run() throws Exception {
    for (String s : getScriptArgs()) {
      Address a = toAddr(Long.decode(s));
      new DisassembleCommand(a, null, true).applyTo(currentProgram, monitor);
      if (getFunctionAt(a) == null && getInstructionAt(a) != null) createFunction(a, null);
      println("force " + a + " -> " + (getFunctionAt(a) != null));
    }
  }
}
