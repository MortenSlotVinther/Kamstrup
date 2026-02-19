#!/usr/bin/env python3
"""Push ONLY the remaining 6 Kamstrup relationship types to OmniGaze demo."""
import json
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

OUTPUT_DIR = r"F:\RootContext\Kamstrup\import-scripts\output"
API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

# ONLY the 6 remaining types (batch 1 already pushed AppToCapability, AppToOrganization, AppToProcess)
REMAINING = [
    ("relationships_CapabilityToValueStream.json",  "CapabilityToValueStream",  223),
    ("relationships_CapabilityToOrganization.json", "CapabilityToOrganization", 1649),
    ("relationships_AppToProvider.json",            "AppToProvider",            803),
    ("relationships_AppToPlatform.json",            "AppToPlatform",            85),
    ("relationships_AppToApp.json",                 "AppToApp",                 34),
    ("relationships_ProcessToValueStream.json",     "ProcessToValueStream",     12),
]

print_lock = threading.Lock()


def push_one(rel, rel_type):
    """Push a single relationship via UpdateFactSheet ParentFactSheetsIds."""
    try:
        child_id = rel["childId"]
        parent_id = rel["parentId"]
        
        result = call_tool("UpdateFactSheet", {
            "id": child_id,
            "updates": {
                "ParentFactSheetsIds": [parent_id]
            }
        }, api_key=API_KEY)

        if isinstance(result, dict) and "error" in result:
            return False, str(result["error"])[:200]

        content = result.get("content", []) if isinstance(result, dict) else []
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text", "")
                    if "success" in text.lower():
                        data = json.loads(text)
                        if data.get("success"):
                            return True, None
                        else:
                            return False, data.get("message", "Unknown error")[:200]
                    elif "error" in text.lower():
                        return False, text[:200]
        
        return True, None
    except Exception as e:
        return False, str(e)[:200]


def push_type(filename, rel_type, expected_count, workers=4, dry_run=False):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found", flush=True)
        return {"type": rel_type, "total": 0, "success": 0, "failed": 0}

    with open(filepath, "r", encoding="utf-8") as f:
        rels = json.load(f)

    total = len(rels)
    print(f"\n{'='*60}", flush=True)
    print(f"{rel_type}: {total} relationships ({workers} workers)", flush=True)
    print(f"{'='*60}", flush=True)

    if dry_run:
        print(f"  [DRY RUN] {total} items", flush=True)
        return {"type": rel_type, "total": total, "success": 0, "failed": 0}

    ok = 0
    fail = 0
    failures = []
    done = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(push_one, r, rel_type): (i, r) for i, r in enumerate(rels)}
        for f in as_completed(futs):
            i, r = futs[f]
            success, err = f.result()
            if success:
                ok += 1
            else:
                fail += 1
                failures.append({"i": i, "p": r.get("parentId"), "c": r.get("childId"), "err": err})
                if fail >= 15 and ok == 0:
                    print(f"  !! Aborting {rel_type}: {fail} failures, 0 ok. Last: {err}", flush=True)
                    pool.shutdown(wait=False, cancel_futures=True)
                    break
            done += 1
            if done % 50 == 0 or done == total:
                elapsed = time.time() - start
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                print(f"  [{done}/{total}] ok={ok} fail={fail} ({rate:.1f}/s, ETA {eta:.0f}s)", flush=True)

    elapsed = time.time() - start
    print(f"  Done: {ok} ok, {fail} fail in {elapsed:.1f}s", flush=True)

    if failures:
        log_path = os.path.join(OUTPUT_DIR, f"push_failures_{rel_type}.json")
        with open(log_path, "w") as fh:
            json.dump(failures[:50], fh, indent=2)
        print(f"  Failures logged: {log_path}", flush=True)

    return {"type": rel_type, "total": total, "success": ok, "failed": fail, "elapsed": round(elapsed, 1)}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--type", type=str, help="Push only one type")
    args = parser.parse_args()

    print("=" * 60, flush=True)
    print("Kamstrup Batch 2: Push Remaining 6 Relationship Types", flush=True)
    print(f"Target: {os.environ['OMNIGAZE_MCP_URL']}", flush=True)
    print(f"Workers: {args.workers}", flush=True)
    print("=" * 60, flush=True)

    # Connectivity test
    print("\nTesting MCP...", flush=True)
    test = call_tool("GetFactSheetSchema", {"factSheetTypeName": "Application"}, api_key=API_KEY)
    if isinstance(test, dict) and "error" in test:
        print(f"FAIL: {test['error']}", flush=True)
        return 1
    print("OK", flush=True)

    results = []
    grand_start = time.time()

    for filename, rel_type, expected in REMAINING:
        if args.type and args.type != rel_type:
            continue
        r = push_type(filename, rel_type, expected, args.workers, args.dry_run)
        results.append(r)

    grand_elapsed = time.time() - grand_start

    print(f"\n{'='*60}", flush=True)
    print("SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"{'Type':<30} {'Total':>6} {'OK':>6} {'Fail':>6} {'Time':>8}", flush=True)
    print("-" * 56, flush=True)
    total_ok = 0
    total_fail = 0
    total_n = 0
    for r in results:
        t = f"{r.get('elapsed', 0)}s"
        print(f"{r['type']:<30} {r['total']:>6} {r['success']:>6} {r['failed']:>6} {t:>8}", flush=True)
        total_ok += r['success']
        total_fail += r['failed']
        total_n += r['total']
    print("-" * 56, flush=True)
    print(f"{'TOTAL':<30} {total_n:>6} {total_ok:>6} {total_fail:>6} {grand_elapsed:.0f}s", flush=True)
    print("=" * 60, flush=True)

    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
