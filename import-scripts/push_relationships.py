#!/usr/bin/env python3
"""
Push Kamstrup relationships to OmniGaze demo via MCP.

Reads relationship JSON files and pushes each relationship using:
- LinkApplicationToBusinessCapability for App->BC
- UpdateFactSheet with ParentFactSheetsIds for all other types

Usage: python push_relationships.py [--dry-run] [--type TYPE] [--test] [--workers N]
"""

import json
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Set env vars BEFORE importing mcp_client (it reads them at module level)
os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

# Configuration
OUTPUT_DIR = r"F:\RootContext\Kamstrup\import-scripts\output"
MCP_URL = os.environ["OMNIGAZE_MCP_URL"]
API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

# Property name used for parent linking
PARENT_PROPERTY = "ParentFactSheetsIds"

# Relationship files in push order
RELATIONSHIP_FILES = [
    ("relationships_AppToCapability.json",          "AppToCapability"),
    ("relationships_AppToOrganization.json",        "AppToOrganization"),
    ("relationships_AppToProcess.json",             "AppToProcess"),
    ("relationships_CapabilityToValueStream.json",  "CapabilityToValueStream"),
    ("relationships_CapabilityToOrganization.json", "CapabilityToOrganization"),
    ("relationships_AppToProvider.json",            "AppToProvider"),
    ("relationships_AppToPlatform.json",            "AppToPlatform"),
    ("relationships_AppToApp.json",                 "AppToApp"),
    ("relationships_ProcessToValueStream.json",     "ProcessToValueStream"),
]

# Thread-safe counters
print_lock = threading.Lock()


def push_one(rel: dict, rel_type: str) -> tuple:
    """Push a single relationship. Returns (success, error_msg_or_None)."""
    try:
        if rel_type == "AppToCapability":
            result = call_tool("LinkApplicationToBusinessCapability", {
                "applicationId": rel["childId"],
                "businessCapabilityId": rel["parentId"]
            }, api_key=API_KEY)
        else:
            result = call_tool("UpdateFactSheet", {
                "id": rel["childId"],
                "updates": {
                    PARENT_PROPERTY: [rel["parentId"]]
                }
            }, api_key=API_KEY)

        # Check for errors
        if isinstance(result, dict) and "error" in result:
            return False, str(result["error"])[:200]

        # Check content for error messages
        content = result.get("content", []) if isinstance(result, dict) else []
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text", "")
                    if isinstance(text, str) and "error" in text.lower() and "success" not in text.lower():
                        return False, text[:200]

        return True, None
    except Exception as e:
        return False, str(e)[:200]


def push_file(filepath: str, rel_type: str, dry_run: bool = False, max_items: int = None, workers: int = 4) -> dict:
    """Push all relationships from one file. Returns summary dict."""
    with open(filepath, "r", encoding="utf-8") as f:
        relationships = json.load(f)

    if max_items:
        relationships = relationships[:max_items]

    total = len(relationships)
    success_count = 0
    fail_count = 0
    failures = []
    start_time = time.time()

    print(f"\n{'='*60}")
    print(f"Processing: {rel_type} ({total} relationships, {workers} workers)")
    print(f"{'='*60}")

    if dry_run:
        print(f"  [DRY RUN] Would push {total} {rel_type} relationships")
        return {"type": rel_type, "total": total, "success": 0, "failed": 0, "failures": [], "dry_run": True}

    # Use thread pool for parallel pushing
    done_count = 0

    def report_progress():
        nonlocal done_count
        done_count += 1
        if done_count % 50 == 0 or done_count == total:
            elapsed = time.time() - start_time
            rate = done_count / elapsed if elapsed > 0 else 0
            eta = (total - done_count) / rate if rate > 0 else 0
            with print_lock:
                print(f"  [{done_count}/{total}] ok={success_count} fail={fail_count} "
                      f"({rate:.1f}/s, ETA {eta:.0f}s)", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_idx = {}
        for i, rel in enumerate(relationships):
            future = executor.submit(push_one, rel, rel_type)
            future_to_idx[future] = (i, rel)

        for future in as_completed(future_to_idx):
            i, rel = future_to_idx[future]
            success, err = future.result()

            if success:
                success_count += 1
            else:
                fail_count += 1
                failures.append({
                    "index": i,
                    "parentId": rel.get("parentId", "?"),
                    "childId": rel.get("childId", "?"),
                    "error": err
                })

                # Early abort on systemic failures
                if fail_count >= 10 and success_count == 0:
                    with print_lock:
                        print(f"  !! 10 consecutive failures, 0 successes - aborting {rel_type}")
                        print(f"     Last error: {err}")
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

            report_progress()

    elapsed = time.time() - start_time
    print(f"  Done in {elapsed:.1f}s ({success_count} ok, {fail_count} failed)")

    return {
        "type": rel_type,
        "total": total,
        "success": success_count,
        "failed": fail_count,
        "elapsed_s": round(elapsed, 1),
        "failures": failures[:30]  # Keep first 30 for log
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Push Kamstrup relationships to OmniGaze")
    parser.add_argument("--dry-run", action="store_true", help="Don't push, just show what would happen")
    parser.add_argument("--type", type=str, help="Only push specific type (e.g., AppToCapability)")
    parser.add_argument("--test", action="store_true", help="Test with 3 items per type")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    args = parser.parse_args()

    print("=" * 60)
    print("Kamstrup Relationship Push to OmniGaze Demo")
    print(f"MCP URL: {MCP_URL}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Workers: {args.workers}")
    if args.dry_run:
        print("MODE: DRY RUN")
    if args.test:
        print("MODE: TEST (3 items per type)")
    print("=" * 60)

    # Test connectivity
    print("\nTesting MCP connectivity...")
    test_result = call_tool("GetFactSheetSchema", {"factSheetTypeName": "Application"}, api_key=API_KEY)
    if isinstance(test_result, dict) and "error" in test_result:
        print(f"FAIL: MCP connection failed: {test_result['error']}")
        return 1
    print("OK: MCP connection working")

    all_summaries = []
    total_pushed = 0
    total_failed = 0
    total_items = 0
    grand_start = time.time()

    for filename, rel_type in RELATIONSHIP_FILES:
        if args.type and args.type != rel_type:
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"\n  SKIP: File not found: {filepath}")
            continue

        max_items = 3 if args.test else None
        summary = push_file(filepath, rel_type, args.dry_run, max_items, args.workers)

        all_summaries.append(summary)
        total_pushed += summary["success"]
        total_failed += summary["failed"]
        total_items += summary["total"]

    grand_elapsed = time.time() - grand_start

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"{'Type':<35} {'Total':>6} {'OK':>6} {'Fail':>6} {'Time':>8}")
    print("-" * 65)
    for s in all_summaries:
        dr = " (dry)" if s.get("dry_run") else ""
        t = f"{s.get('elapsed_s', 0)}s"
        print(f"{s['type']:<35} {s['total']:>6} {s['success']:>6} {s['failed']:>6} {t:>8}{dr}")
    print("-" * 65)
    print(f"{'TOTAL':<35} {total_items:>6} {total_pushed:>6} {total_failed:>6} {grand_elapsed:.0f}s")
    print("=" * 60)

    # Log failures
    if total_failed > 0:
        fail_log = os.path.join(OUTPUT_DIR, "push_failures.json")
        all_failures = []
        for s in all_summaries:
            for f in s.get("failures", []):
                f["type"] = s["type"]
                all_failures.append(f)
        with open(fail_log, "w", encoding="utf-8") as fh:
            json.dump(all_failures, fh, indent=2)
        print(f"\nFailure details: {fail_log}")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
