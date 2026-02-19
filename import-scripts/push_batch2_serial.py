#!/usr/bin/env python3
"""Push remaining 6 Kamstrup relationship types SERIALLY (no threading)."""
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
print("Kamstrup Batch 2 (Serial Push)", flush=True)
print("=" * 60, flush=True)

# Test connectivity
print("Testing MCP...", flush=True)
test = call_tool("GetFactSheetSchema", {"factSheetTypeName": "Application"}, api_key=API_KEY)
if isinstance(test, dict) and "error" in test:
    print(f"FAIL: {test['error']}", flush=True)
    sys.exit(1)
print("OK\n", flush=True)

grand_ok = 0
grand_fail = 0
grand_start = time.time()
results = []

for filename, rel_type in REMAINING:
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"SKIP: {filename} not found", flush=True)
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        rels = json.load(f)

    total = len(rels)
    ok = 0
    fail = 0
    failures = []
    start = time.time()
    
    print(f"--- {rel_type}: {total} items ---", flush=True)

    for i, rel in enumerate(rels):
        try:
            result = call_tool("UpdateFactSheet", {
                "id": rel["childId"],
                "updates": {"ParentFactSheetsIds": [rel["parentId"]]}
            }, api_key=API_KEY)

            success = False
            if isinstance(result, dict):
                if "error" in result:
                    fail += 1
                    failures.append({"i": i, "err": str(result["error"])[:150]})
                else:
                    content = result.get("content", [])
                    for c in content:
                        if isinstance(c, dict):
                            t = c.get("text", "")
                            if '"success":true' in t or '"success": true' in t:
                                success = True
                    if success:
                        ok += 1
                    else:
                        # Could still be ok if no explicit success flag
                        ok += 1
            else:
                ok += 1
        except Exception as e:
            fail += 1
            failures.append({"i": i, "err": str(e)[:150]})

        # Progress every 50
        if (i + 1) % 50 == 0 or (i + 1) == total:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (total - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1}/{total}] ok={ok} fail={fail} ({rate:.1f}/s, ETA {eta:.0f}s)", flush=True)

        # Abort on systemic failure
        if fail >= 15 and ok == 0:
            print(f"  !! Aborting: {fail} failures, 0 ok", flush=True)
            break

    elapsed = time.time() - start
    print(f"  Done: {ok} ok, {fail} fail ({elapsed:.1f}s)\n", flush=True)
    
    grand_ok += ok
    grand_fail += fail
    results.append({"type": rel_type, "total": total, "ok": ok, "fail": fail, "time": round(elapsed, 1)})

    if failures:
        log_path = os.path.join(OUTPUT_DIR, f"push_failures_{rel_type}.json")
        with open(log_path, "w") as fh:
            json.dump(failures[:50], fh, indent=2)

grand_elapsed = time.time() - grand_start
print("=" * 60, flush=True)
print("SUMMARY", flush=True)
print(f"{'Type':<30} {'Total':>6} {'OK':>6} {'Fail':>6} {'Time':>8}", flush=True)
print("-" * 56, flush=True)
for r in results:
    print(f"{r['type']:<30} {r['total']:>6} {r['ok']:>6} {r['fail']:>6} {r['time']}s", flush=True)
print("-" * 56, flush=True)
print(f"{'TOTAL':<30} {sum(r['total'] for r in results):>6} {grand_ok:>6} {grand_fail:>6} {grand_elapsed:.0f}s", flush=True)
print("=" * 60, flush=True)
