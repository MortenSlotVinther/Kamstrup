#!/usr/bin/env python3
"""Test CreateFactSheet with correct parameter names."""
import os, sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

# Try with proper initialProperties
print("Test 1: factSheetType + initialProperties", flush=True)
result = call_tool("CreateFactSheet", {
    "factSheetType": "Application",
    "initialProperties": {
        "DisplayName": "TEST-DELETE-ME"
    }
}, api_key=API_KEY)
print("Result:", json.dumps(result, indent=2, default=str)[:500], flush=True)

# Also check LinkApplicationToBusinessCapability tool definition
print("\nListing LinkApp tool...", flush=True)
from mcp_client import list_tools
tools = list_tools(api_key=API_KEY)
if "tools" in tools:
    for t in tools["tools"]:
        if "Link" in t.get("name", ""):
            print(f"  {t['name']}: {json.dumps(t.get('inputSchema',{}).get('properties',{}), indent=2)[:300]}", flush=True)
