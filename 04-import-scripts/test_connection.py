#!/usr/bin/env python3
"""Quick MCP connection test."""
import os, sys, time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

print("Testing MCP connection to demo.omnigaze.com...", flush=True)
start = time.time()
result = call_tool("GetFactSheetSchema", {"factSheetTypeName": "Application"}, api_key=API_KEY)
elapsed = time.time() - start

if isinstance(result, dict) and "error" in result:
    print("FAIL (%.1fs): %s" % (elapsed, result["error"]), flush=True)
else:
    print("OK (%.1fs)" % elapsed, flush=True)
    
# Try a second call
print("Second call...", flush=True)
start = time.time()
result2 = call_tool("CreateFactSheet", {
    "factSheetTypeName": "Application",
    "displayName": "TEST-DELETE-ME"
}, api_key=API_KEY)
elapsed2 = time.time() - start

if isinstance(result2, dict) and "error" in result2:
    print("FAIL (%.1fs): %s" % (elapsed2, result2["error"]), flush=True)
else:
    print("OK (%.1fs): %s" % (elapsed2, str(result2)[:200]), flush=True)
