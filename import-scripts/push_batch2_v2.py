#!/usr/bin/env python3
"""Push remaining 6 Kamstrup relationship types SERIALLY (no threading, no argparse)."""
import json, os, sys, time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

OUTPUT_DIR = r"F:\RootContext\Kamstrup\import-scripts\output"
API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

REMAINING = [
    ("relationships_CapabilityToValueStream.json",  "CapabilityToValueStream"),
    ("relationships_CapabilityToOrganization.json", "CapabilityToOrganization"),
    ("relationships_AppToProvider.json",            "AppToProvider"),
    ("relationships_AppToPlatform.json",            "AppToPlatform"),
    ("relationships_AppToApp.json",                 "AppToApp"),
    ("relationships_ProcessToValueStream.json",     "ProcessToValueStream"),
]

print("=" * 60, flush=True)
print("Kamstrup Batch 2 (Serial v2)", flush=True)
print("=" * 60, flush=True)

# Test
print("Testing MCP...", flush=True)
test = call_tool("GetFactSheetSchema", {"factSheetTypeName": "Application"}, api_key=API_KEY)
if isinstance(test, dict) and "error" in test:
    print("FAIL: " + str(test["error"]), flush=True)
    sys.exit(1)
print("OK\n", flush=True)

grand_ok = 0
grand_fail = 0
grand_start = time.time()
results = []

for filename, rel_type in REMAINING:
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        print("SKIP: " + filename, flush=True)
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        rels = json.load(f)

    total = len(rels)
    ok = 0
    fail = 0
    start = time.time()
    
    print("--- " + rel_type + ": " + str(total) + " items ---", flush=True)

    for i in range(total):
        rel = rels[i]
        try:
            result = call_tool("UpdateFactSheet", {
                "id": rel["childId"],
                "updates": {"ParentFactSheetsIds": [rel["parentId"]]}
            }, api_key=API_KEY)

            if isinstance(result, dict) and "error" in result:
                fail += 1
            else:
                ok += 1
        except Exception as e:
            fail += 1

        done = i + 1
        if done % 50 == 0 or done == total:
            elapsed = time.time() - start
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate if rate > 0 else 0
            print("  [" + str(done) + "/" + str(total) + "] ok=" + str(ok) + " fail=" + str(fail) + " (" + "{:.1f}".format(rate) + "/s, ETA " + "{:.0f}".format(eta) + "s)", flush=True)

        if fail >= 15 and ok == 0:
            print("  !! Aborting: too many failures", flush=True)
            break

    elapsed = time.time() - start
    print("  Done: " + str(ok) + " ok, " + str(fail) + " fail (" + "{:.1f}".format(elapsed) + "s)\n", flush=True)
    
    grand_ok += ok
    grand_fail += fail
    results.append({"type": rel_type, "total": total, "ok": ok, "fail": fail, "time": round(elapsed, 1)})

grand_elapsed = time.time() - grand_start
print("=" * 60, flush=True)
print("SUMMARY", flush=True)
print("=" * 60, flush=True)
for r in results:
    print(r["type"] + ": " + str(r["ok"]) + "/" + str(r["total"]) + " ok, " + str(r["fail"]) + " fail, " + str(r["time"]) + "s", flush=True)
print("TOTAL: " + str(grand_ok) + " ok, " + str(grand_fail) + " fail in " + "{:.0f}".format(grand_elapsed) + "s", flush=True)
print("=" * 60, flush=True)
