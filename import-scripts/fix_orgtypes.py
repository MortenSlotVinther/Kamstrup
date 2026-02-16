#!/usr/bin/env python3
"""
Fix OrgType for all Organization FactSheets in OmniGaze.

Root cause: push_to_omnigaze.py never passed OrgType when creating factsheets,
so all 210 orgs got the default "Enterprise" value.

This script:
1. Gets all Organization factsheets via MCP
2. Determines correct OrgType from hierarchy level
3. Updates each one via MCP UpdateFactSheet

Uses the MCP client SSE transport directly.
"""

import json
import os
import sys
import threading
import time
import uuid
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

MCP_BASE = os.environ.get("OMNIGAZE_MCP_URL", "http://localhost:5000")
MCP_SSE_URL = MCP_BASE + "/mcp/sse"
API_KEY = os.environ.get("OMNIGAZE_MCP_API_KEY", "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo=")


def mcp_call(method: str, params: dict = None, timeout: int = 30) -> dict:
    """Call MCP server via SSE transport with persistent connection."""
    request_id = str(uuid.uuid4())
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params:
        payload["params"] = params

    result_holder = {"result": None, "error": None}
    message_url_holder = {"url": None}
    ready_event = threading.Event()
    done_event = threading.Event()

    def sse_reader():
        try:
            headers = {
                "Accept": "text/event-stream",
                "User-Agent": "OrgType-Fix/1.0",
                "X-API-Key": API_KEY,
            }
            req = Request(MCP_SSE_URL, headers=headers, method="GET")
            with urlopen(req, timeout=timeout) as response:
                current_event = None
                for raw_line in response:
                    line = raw_line.decode('utf-8').strip()
                    if line.startswith('event:'):
                        current_event = line[6:].strip()
                    elif line.startswith('data:'):
                        data_str = line[5:].strip()
                        if current_event == 'endpoint' or (message_url_holder["url"] is None and '?sessionId=' in data_str):
                            if data_str.startswith('/'):
                                message_url_holder["url"] = MCP_BASE + data_str
                            else:
                                message_url_holder["url"] = data_str
                            ready_event.set()
                        elif current_event == 'message' or message_url_holder["url"] is not None:
                            try:
                                data = json.loads(data_str)
                                if data.get("id") == request_id:
                                    if "result" in data:
                                        result_holder["result"] = data["result"]
                                    else:
                                        result_holder["result"] = data
                                    done_event.set()
                                    return
                            except json.JSONDecodeError:
                                pass
                        current_event = None
                    if done_event.is_set():
                        return
        except Exception as e:
            result_holder["error"] = str(e)
            ready_event.set()
            done_event.set()

    sse_thread = threading.Thread(target=sse_reader, daemon=True)
    sse_thread.start()

    if not ready_event.wait(timeout=timeout):
        return {"error": "Timeout waiting for SSE session URL"}

    if result_holder["error"]:
        return {"error": result_holder["error"]}

    message_url = message_url_holder["url"]
    if not message_url:
        return {"error": "No session URL received"}

    post_headers = {
        "Content-Type": "application/json",
        "User-Agent": "OrgType-Fix/1.0",
        "X-API-Key": API_KEY,
    }

    req = Request(
        message_url,
        data=json.dumps(payload).encode('utf-8'),
        headers=post_headers,
        method="POST"
    )

    try:
        with urlopen(req, timeout=timeout) as response:
            post_content = response.read().decode('utf-8')
            if post_content.strip():
                for pline in post_content.split('\n'):
                    if pline.startswith('data:'):
                        try:
                            data = json.loads(pline[5:].strip())
                            if 'result' in data:
                                return data['result']
                            return data
                        except json.JSONDecodeError:
                            continue
                try:
                    data = json.loads(post_content)
                    if 'result' in data:
                        return data['result']
                    return data
                except json.JSONDecodeError:
                    pass
    except HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}

    # Wait for SSE response
    if done_event.wait(timeout=timeout):
        if result_holder["result"] is not None:
            return result_holder["result"]
    return {"error": "Timeout waiting for response"}


def call_tool(tool_name: str, arguments: dict) -> dict:
    return mcp_call("tools/call", {"name": tool_name, "arguments": arguments})


def main():
    print("=" * 60)
    print("OrgType Fix Script")
    print(f"MCP server: {MCP_BASE}")
    print("=" * 60)

    # Step 1: List tools to verify connection
    print("\n[1] Verifying MCP connection...")
    tools_result = mcp_call("tools/list")
    if "error" in tools_result:
        print(f"  ERROR: {tools_result['error']}")
        print("  Is OmniGaze running at {MCP_BASE}?")
        sys.exit(1)
    
    tool_names = []
    if "tools" in tools_result:
        tool_names = [t["name"] for t in tools_result["tools"]]
    print(f"  Available tools: {tool_names}")

    # Step 2: Get all factsheets
    print("\n[2] Getting all Organization factsheets...")
    result = call_tool("GetAllFactSheets", {})
    
    if "error" in result:
        print(f"  ERROR: {result['error']}")
        sys.exit(1)

    # Parse the result - MCP returns content array
    factsheets = []
    if isinstance(result, dict) and "content" in result:
        for item in result["content"]:
            if item.get("type") == "text":
                try:
                    factsheets = json.loads(item["text"])
                except json.JSONDecodeError:
                    pass
    elif isinstance(result, list):
        factsheets = result

    # Filter to organizations only
    orgs = [fs for fs in factsheets if fs.get("factSheetType", "").lower().replace("factsheet", "") == "organization" 
            or fs.get("FactSheetType", "") == "OrganizationFactSheet"
            or fs.get("factSheetTypeName", "") == "Organization"]
    
    print(f"  Total factsheets: {len(factsheets)}")
    print(f"  Organization factsheets: {len(orgs)}")

    if not orgs:
        print("  No organization factsheets found!")
        print("  Sample data from first few factsheets:")
        for fs in factsheets[:3]:
            print(f"    {json.dumps(fs, indent=2)[:200]}")
        sys.exit(1)

    # Step 3: Build hierarchy and determine levels
    print("\n[3] Analyzing hierarchy to determine OrgType per org...")

    # Build parent-child map
    id_map = {fs.get("id", fs.get("Id")): fs for fs in orgs}
    
    # Find roots (no parent or parent not in org set)
    def get_level(fs, depth=0):
        """Recursively determine hierarchy level."""
        if depth > 10:
            return depth  # safety valve
        parent_id = fs.get("hierarchyParentId") or fs.get("HierarchyParentId")
        if not parent_id or parent_id not in id_map:
            return 1  # root = Country
        return 1 + get_level(id_map[parent_id], depth + 1)

    level_to_orgtype = {
        1: "Country",
        2: "Business Unit",
        3: "Department",
        4: "Team",
    }

    updates = []
    for org in orgs:
        org_id = org.get("id") or org.get("Id")
        org_name = org.get("displayName") or org.get("DisplayName") or "?"
        current_type = org.get("orgType") or org.get("OrgType") or "?"
        level = get_level(org)
        new_type = level_to_orgtype.get(level, "Team")  # default to Team for deeper levels
        
        if current_type != new_type:
            updates.append({
                "id": org_id,
                "name": org_name,
                "current": current_type,
                "new": new_type,
                "level": level,
            })

    print(f"  Need to update: {len(updates)} organizations")
    
    # Show summary by level
    from collections import Counter
    level_counts = Counter(u["level"] for u in updates)
    for level in sorted(level_counts.keys()):
        print(f"    Level {level} ({level_to_orgtype.get(level, '?')}): {level_counts[level]} orgs")

    # Show sample
    if updates:
        print(f"\n  Sample updates:")
        for u in updates[:5]:
            print(f"    {u['name']}: {u['current']} → {u['new']} (L{u['level']})")

    # Step 4: Apply updates
    print(f"\n[4] Applying {len(updates)} OrgType updates...")
    
    success = 0
    failed = 0
    for i, u in enumerate(updates):
        result = call_tool("UpdateFactSheet", {
            "id": u["id"],
            "updates": {"OrgType": u["new"]}
        })
        
        if isinstance(result, dict) and "error" in result:
            print(f"  ✗ Failed [{i+1}/{len(updates)}] {u['name']}: {result['error']}")
            failed += 1
        else:
            success += 1
            if (i + 1) % 20 == 0 or (i + 1) == len(updates):
                print(f"  ✓ Updated {i+1}/{len(updates)}...")
        
        time.sleep(0.05)  # rate limit

    print(f"\n{'='*60}")
    print(f"COMPLETE: {success} updated, {failed} failed out of {len(updates)} total")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
