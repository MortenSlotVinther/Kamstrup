#!/usr/bin/env python3
"""Quick check of factsheet counts on demo."""
import os, sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

# Get BCs
result = call_tool("GetBusinessCapabilityFactSheets", {}, api_key=API_KEY)
content = result.get("content", []) if isinstance(result, dict) else []
for item in (content if isinstance(content, list) else []):
    if isinstance(item, dict):
        text = item.get("text", "")
        try:
            data = json.loads(text)
            if isinstance(data, list):
                print("BCs: %d" % len(data), flush=True)
            elif isinstance(data, dict) and "factSheets" in data:
                print("BCs: %d" % len(data["factSheets"]), flush=True)
            else:
                print("BC result: %s" % str(data)[:200], flush=True)
        except:
            print("BC text: %s" % text[:200], flush=True)

# Get all factsheets via GraphQL
result2 = call_tool("ExecuteAssetGraphQLQuery", {
    "query": "{ applicationFactSheets { totalCount } businessCapabilityFactSheets { totalCount } valueStreamFactSheets { totalCount } organizationFactSheets { totalCount } processFactSheets { totalCount } }"
}, api_key=API_KEY)
content2 = result2.get("content", []) if isinstance(result2, dict) else []
for item in (content2 if isinstance(content2, list) else []):
    if isinstance(item, dict):
        print("GraphQL: %s" % item.get("text", "")[:500], flush=True)
