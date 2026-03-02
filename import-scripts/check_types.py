#!/usr/bin/env python3
"""Check available factsheet types."""
import os, sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

# Try various type names
types_to_test = [
    "Application", "BusinessCapability", "ValueStream", "ValueStreamFactSheet",
    "Organization", "Process", "ITComponent", "Provider",
    "DataObject", "TechnologyService", "Interface",
    "ProviderFactSheet", "OrganizationFactSheet"
]

for t in types_to_test:
    result = call_tool("GetFactSheetSchema", {"factSheetTypeName": t}, api_key=API_KEY)
    content = result.get("content", []) if isinstance(result, dict) else []
    status = "?"
    for item in (content if isinstance(content, list) else []):
        if isinstance(item, dict):
            text = item.get("text", "")
            if "not found" in text.lower() or "not supported" in text.lower():
                status = "NOT FOUND"
            elif "properties" in text.lower() or "schema" in text.lower() or "displayName" in text.lower():
                status = "OK"
            else:
                status = text[:80]
    print("%-30s %s" % (t, status), flush=True)
