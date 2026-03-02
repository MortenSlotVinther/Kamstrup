#!/usr/bin/env python3
import os, sys, json
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="
sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool
API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

types = ["Provider", "ProviderFactSheet", "OrganizationFactSheet"]
for t in types:
    r = call_tool("GetFactSheetSchema", {"factSheetTypeName": t}, api_key=API_KEY)
    content = r.get("content", []) if isinstance(r, dict) else []
    status = "?"
    for item in (content if isinstance(content, list) else []):
        if isinstance(item, dict):
            text = item.get("text", "")
            if "not found" in text.lower() or "not supported" in text.lower():
                status = "NOT FOUND"
            elif len(text) > 50:
                status = "OK"
            else:
                status = text[:80]
    print("%-30s %s" % (t, status), flush=True)
