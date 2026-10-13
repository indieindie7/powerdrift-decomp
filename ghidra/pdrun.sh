#!/bin/bash
# headless Ghidra on the PowerDrift project. usage: pdrun.sh <log> [headless args after project name]
# Set GHIDRA_HEADLESS (path to analyzeHeadless) and PD_GHIDRA (folder holding PowerDrift.gpr).
log="$1"; shift
"$GHIDRA_HEADLESS" "$PD_GHIDRA" PowerDrift "$@" > "$log" 2>&1
tail -3 "$log"
