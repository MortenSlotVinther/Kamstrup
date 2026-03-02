#!/usr/bin/env python3
"""Test CreateFactSheet with correct parameter name."""
import os, sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool, list_tools

API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

# First list tools to see parameter names
print("Listing tools...", flush=True)
tools = list_tools(api_key=API_KEY)
# Find CreateFactSheet
if "tools" in tools:
    for t in tools["tools"]:
        if t.get("name") == "CreateFactSheet":
            print(json.dumps(t, indent=2), flush=True)
            break
else:
    print("Tools response:", json.dumps(tools, indent=2)[:500], flush=True)

# Try with factSheetType instead of factSheetTypeName
print("\nTrying factSheetType...", flush=True)
result = call_tool("CreateFactSheet", {
    "factSheetType": "Application",
    "displayName": "TEST-DELETE-ME"
}, api_key=API_KEY)
print("Result:", json.dumps(result, indent=2, default=str)[:500], flush=True)
