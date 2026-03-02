#!/usr/bin/env python3
"""Push Kamstrup applications to OmniGaze demo via MCP (serial)."""
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

def main():
    # Load active applications
    with open(os.path.join(OUTPUT_DIR, "applications_active.json"), "r", encoding="utf-8") as f:
        apps = json.load(f)
    
    # Also load retired apps
    retired_path = os.path.join(OUTPUT_DIR, "applications_removed.json")
    if os.path.exists(retired_path):
        with open(retired_path, "r", encoding="utf-8") as f:
            retired = json.load(f)
        print(f"Loaded {len(apps)} active + {len(retired)} retired applications", flush=True)
        apps.extend(retired)
    else:
        print(f"Loaded {len(apps)} active applications (no retired file)", flush=True)
    
    total = len(apps)
    ok = 0
    fail = 0
    start = time.time()
    
    print(f"Pushing {total} applications to OmniGaze demo...", flush=True)
    print("=" * 60, flush=True)
    
    for i, app in enumerate(apps):
        create_args = {
            "factSheetTypeName": "Application",
            "displayName": app["DisplayName"],
        }
        
        if app.get("RichDescription"):
            create_args["richDescription"] = app["RichDescription"]
        if app.get("Responsible"):
            create_args["responsible"] = app["Responsible"]
        if app.get("Url"):
            create_args["url"] = app["Url"]
        if app.get("Category"):
            create_args["category"] = app["Category"]
        
        try:
            result = call_tool("CreateFactSheet", create_args, api_key=API_KEY)
            
            if isinstance(result, dict) and "error" in result:
                fail += 1
                if fail <= 5:
                    print(f"  FAIL [{i}]: {app['DisplayName']}: {str(result['error'])[:100]}", flush=True)
            else:
                ok += 1
        except Exception as e:
            fail += 1
            if fail <= 5:
                print(f"  ERROR [{i}]: {app['DisplayName']}: {str(e)[:100]}", flush=True)
        
        done = i + 1
        if done % 50 == 0 or done == total:
            elapsed = time.time() - start
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate if rate > 0 else 0
            print(f"  [{done}/{total}] ok={ok} fail={fail} ({rate:.1f}/s, ETA {eta:.0f}s)", flush=True)
        
        if fail >= 15 and ok == 0:
            print("  !! Aborting: too many failures, 0 successes", flush=True)
            break
    
    elapsed = time.time() - start
    print("=" * 60, flush=True)
    print(f"DONE: {ok} created, {fail} failed in {elapsed:.1f}s", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
