// PdDelete.java <list.txt|addrs...>: remove false functions (data decoded as code) and clear their instructions.
// A .txt arg is read as lines `0x<addr> ...` (# = comment). Prints how many were removed.
//@category PowerDrift
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.nio.file.*;
import java.util.*;
public class PdDelete extends GhidraScript {
  public void run() throws Exception {
    List<String> addrs = new ArrayList<>();
    for (String s : getScriptArgs()) {
      if (s.endsWith(".txt")) {
        for (String ln : Files.readAllLines(Paths.get(s))) {
          ln = ln.trim();
          if (!ln.isEmpty() && !ln.startsWith("#")) addrs.add(ln.split("\\s+")[0]);
        }
      } else addrs.add(s);
    }
    int n = 0;
    for (String s : addrs) {
      Address a = toAddr(Long.decode(s));
      Function f = getFunctionAt(a);
      if (f == null) continue;
      Address end = f.getBody().getMaxAddress();
      removeFunction(f);
      clearListing(a, end);
      n++;
    }
    println("PdDelete removed " + n);
  }
}
