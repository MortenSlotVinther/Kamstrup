#!/usr/bin/env python3
"""Debug a single CreateFactSheet call."""
import os, sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

# Test 1: Simple BC
print("=== Test 1: Create BC ===", flush=True)
r1 = call_tool("CreateFactSheet", {
    "factSheetType": "BusinessCapability",
    "initialProperties": {"DisplayName": "Test BC 001"}
}, api_key=API_KEY)
print("Result: %s" % json.dumps(r1, indent=2, default=str)[:500], flush=True)

# Test 2: ValueStream
print("\n=== Test 2: Create ValueStream ===", flush=True)
r2 = call_tool("CreateFactSheet", {
    "factSheetType": "ValueStream",
    "initialProperties": {"DisplayName": "Test VS 001"}
}, api_key=API_KEY)
print("Result: %s" % json.dumps(r2, indent=2, default=str)[:500], flush=True)

# Test 3: Check what we have
print("\n=== Test 3: Check BCs ===", flush=True)
r3 = call_tool("GetBusinessCapabilityFactSheets", {}, api_key=API_KEY)
content = r3.get("content", []) if isinstance(r3, dict) else []
for item in (content if isinstance(content, list) else []):
    if isinstance(item, dict):
        text = item.get("text", "")
        try:
            data = json.loads(text)
            if isinstance(data, list):
                print("BCs found: %d" % len(data), flush=True)
                for bc in data[:3]:
                    print("  - %s" % bc.get("displayName", "?"), flush=True)
        except:
            print("Text: %s" % text[:200], flush=True)
