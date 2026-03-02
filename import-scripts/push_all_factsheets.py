#!/usr/bin/env python3
"""Push ALL Kamstrup factsheets to OmniGaze demo via MCP.
Uses current API: factSheetType + initialProperties."""
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

TYPE_MAP = {
    "ValueStreamFactSheet": "ValueStreamFactSheet",
    "BusinessCapabilityFactSheet": "BusinessCapability",
    "OrganizationFactSheet": "OrganizationFactSheet",
    "ProcessFactSheet": "Process",
    "ITComponentFactSheet": "ITComponent",
    "ProviderFactSheet": "Provider",
}

BASE_FILES = [
    ("01-value-streams.json", "Value Streams"),
    ("02-business-capabilities.json", "Business Capabilities"),
    ("03-organizations.json", "Organizations"),
    ("04-processes.json", "Processes"),
    ("05-platforms.json", "Platforms (ITComponent)"),
    ("06-providers.json", "Providers"),
]


def is_success(result):
    """Check if MCP call was successful."""
    if not isinstance(result, dict):
        return False
    if result.get("isError"):
        return False
    if "error" in result:
        return False
    content = result.get("content", [])
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                text = item.get("text", "")
                try:
                    data = json.loads(text)
                    if data.get("success"):
                        return True
                except (json.JSONDecodeError, TypeError):
                    pass
                if "success" in text.lower() and "error" not in text.lower():
                    return True
    return True  # No error markers = success


def get_error_text(result):
    """Extract error text from result."""
    if isinstance(result, dict):
        if "error" in result:
            return str(result["error"])[:150]
        content = result.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    return item.get("text", "")[:150]
    return str(result)[:150]


def push_batch(items, type_name, label, get_props_fn):
    """Push a batch of factsheets. Returns (ok, fail)."""
    total = len(items)
    ok = 0
    fail = 0
    start = time.time()

    print("\n--- %s: %d items ---" % (label, total), flush=True)

    for i, item in enumerate(items):
        props = get_props_fn(item)
        try:
            result = call_tool("CreateFactSheet", {
                "factSheetType": type_name,
                "initialProperties": props
            }, api_key=API_KEY)

            if is_success(result):
                ok += 1
            else:
                fail += 1
                if fail <= 3:
                    print("  FAIL [%d] %s: %s" % (i, props.get("DisplayName", "?"), get_error_text(result)), flush=True)
        except Exception as e:
            fail += 1
            if fail <= 3:
                print("  ERR [%d] %s: %s" % (i, props.get("DisplayName", "?"), str(e)[:100]), flush=True)

        done = i + 1
        if done % 50 == 0 or done == total:
            elapsed = time.time() - start
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate if rate > 0 else 0
            print("  [%d/%d] ok=%d fail=%d (%.1f/s, ETA %.0fs)" % (done, total, ok, fail, rate, eta), flush=True)

        if fail >= 20 and ok == 0:
            print("  !! ABORT: %d fails, 0 successes" % fail, flush=True)
            break

    elapsed = time.time() - start
    print("  DONE: %d ok, %d fail (%.1fs)" % (ok, fail, elapsed), flush=True)
    return ok, fail


def main():
    print("=" * 60, flush=True)
    print("Kamstrup Full Import - All Factsheets", flush=True)
    print("Target: %s" % os.environ["OMNIGAZE_MCP_URL"], flush=True)
    print("=" * 60, flush=True)

    # Test
    print("\nTesting MCP...", flush=True)
    t0 = time.time()
    test = call_tool("GetFactSheetSchema", {"factSheetTypeName": "Application"}, api_key=API_KEY)
    if isinstance(test, dict) and "error" in test:
        print("FAIL: %s" % test["error"], flush=True)
        sys.exit(1)
    print("OK (%.1fs)" % (time.time() - t0), flush=True)

    grand_start = time.time()
    grand_ok = 0
    grand_fail = 0

    # Phase 1: Base factsheets
    for filename, label in BASE_FILES:
        filepath = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            print("\nSKIP: %s" % filename, flush=True)
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            factsheets = json.load(f)

        def make_base_props(fs):
            fs_type_key = fs["FactSheetType"]
            props = {"DisplayName": fs["DisplayName"]}
            if fs.get("RichDescription"):
                props["RichDescription"] = fs["RichDescription"]
            if fs.get("Responsible"):
                props["Responsible"] = fs["Responsible"]
            if fs.get("ShortDescription"):
                props["ShortDescription"] = fs["ShortDescription"]
            if fs.get("OrgType"):
                ot = fs["OrgType"]
                props["OrgType"] = "Business Unit" if ot == "BusinessUnit" else ot
            if fs.get("CountryCode"):
                props["CountryCode"] = fs["CountryCode"]
            return props

        fs_type = TYPE_MAP.get(factsheets[0]["FactSheetType"], factsheets[0]["FactSheetType"])
        ok, fail = push_batch(factsheets, fs_type, label, make_base_props)
        grand_ok += ok
        grand_fail += fail

    # Phase 2: Applications
    apps = []
    active_path = os.path.join(OUTPUT_DIR, "applications_active.json")
    if os.path.exists(active_path):
        with open(active_path, "r", encoding="utf-8") as f:
            apps.extend(json.load(f))

    retired_path = os.path.join(OUTPUT_DIR, "applications_removed.json")
    if os.path.exists(retired_path):
        with open(retired_path, "r", encoding="utf-8") as f:
            apps.extend(json.load(f))

    if apps:
        print("\nLoaded %d applications (active + retired)" % len(apps), flush=True)

        def make_app_props(app):
            props = {"DisplayName": app["DisplayName"]}
            if app.get("RichDescription"):
                props["RichDescription"] = app["RichDescription"]
            if app.get("Responsible"):
                props["Responsible"] = app["Responsible"]
            if app.get("Url"):
                props["Url"] = app["Url"]
            if app.get("Category"):
                props["Category"] = app["Category"]
            return props

        ok, fail = push_batch(apps, "Application", "Applications", make_app_props)
        grand_ok += ok
        grand_fail += fail

    grand_elapsed = time.time() - grand_start
    print("\n" + "=" * 60, flush=True)
    print("FINAL: %d ok, %d fail in %.0fs (%.1f/s)" % (
        grand_ok, grand_fail, grand_elapsed,
        (grand_ok + grand_fail) / grand_elapsed if grand_elapsed > 0 else 0
    ), flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
