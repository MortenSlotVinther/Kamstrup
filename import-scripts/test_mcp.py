#!/usr/bin/env python3
"""Quick test: get Application schema to understand ParentFactSheetsIds."""
import sys, os, json
sys.path.insert(0, r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts")
from mcp_client import call_tool

os.environ["OMNIGAZE_MCP_URL"] = "https://demo.omnigaze.com"
os.environ["OMNIGAZE_MCP_API_KEY"] = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="
API_KEY = os.environ["OMNIGAZE_MCP_API_KEY"]

# Test 1: Get Application schema
print("=== Application Schema ===")
result = call_tool("GetFactSheetSchema", {"factSheetTypeName": "Application"}, api_key=API_KEY)
print(json.dumps(result, indent=2)[:3000])

# Test 2: Try LinkApplicationToBusinessCapability with the first AppToCapability relationship
print("\n=== Testing LinkApplicationToBusinessCapability ===")
with open(r"F:\RootContext\Kamstrup\import-scripts\output\relationships_AppToCapability.json", "r") as f:
    rels = json.load(f)
rel = rels[0]
print(f"Linking app={rel['childId']} to bc={rel['parentId']}")
result2 = call_tool("LinkApplicationToBusinessCapability", {
    "applicationId": rel["childId"],
    "businessCapabilityId": rel["parentId"]
}, api_key=API_KEY)
print(json.dumps(result2, indent=2)[:2000])
