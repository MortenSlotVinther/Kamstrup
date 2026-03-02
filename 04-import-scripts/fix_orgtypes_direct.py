#!/usr/bin/env python3
"""
Fix OrgType for all Organization FactSheets in OmniGaze.

This script talks directly to OmniGaze MCP via SSE, gets all org factsheets,
determines correct OrgType from hierarchy, and updates each one.

Uses a persistent SSE connection per request (new session per tool call).
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


def mcp_call_tool(tool_name: str, arguments: dict, timeout: int = 30) -> dict:
    """Call an MCP tool. Opens SSE, gets session, POSTs request, reads response."""
    request_id = str(uuid.uuid4())
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }

    result_holder = {"result": None, "error": None, "done": False}
    message_url_holder = {"url": None}
    ready_event = threading.Event()
    done_event = threading.Event()

    def sse_reader():
        try:
            headers = {
                "Accept": "text/event-stream",
                "User-Agent": "OrgTypeFix/1.0",
                "X-API-Key": API_KEY,
            }
            req = Request(MCP_SSE_URL, headers=headers, method="GET")
            with urlopen(req, timeout=timeout) as response:
                current_event = None
                buffer = ""
                for raw_line in response:
                    line = raw_line.decode('utf-8').rstrip('\r\n')
                    
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
                        elif message_url_holder["url"] is not None:
                            try:
                                data = json.loads(data_str)
                                if isinstance(data, dict) and data.get("id") == request_id:
                                    result_holder["result"] = data.get("result", data)
                                    result_holder["done"] = True
                                    done_event.set()
                                    return
                            except json.JSONDecodeError:
                                pass
                        current_event = None
                    
                    if done_event.is_set():
                        return
        except Exception as e:
            if not done_event.is_set():
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

    # POST the request
    post_headers = {
        "Content-Type": "application/json",
        "User-Agent": "OrgTypeFix/1.0",
        "X-API-Key": API_KEY,
    }

    try:
        req = Request(
            message_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=post_headers,
            method="POST"
        )
        with urlopen(req, timeout=timeout) as response:
            post_content = response.read().decode('utf-8')
            if post_content.strip():
                # Check if response came in POST body
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
        body = ""
        try:
            body = e.read().decode('utf-8')
        except:
            pass
        return {"error": f"HTTP {e.code}: {e.reason} - {body}"}

    # Wait for SSE response
    if done_event.wait(timeout=timeout):
        if result_holder["result"] is not None:
            return result_holder["result"]
    
    return {"error": "Timeout waiting for response"}


def extract_factsheets(result):
    """Extract factsheet list from MCP result."""
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        if "error" in result:
            return None
        if "content" in result:
            for item in result["content"]:
                if isinstance(item, dict) and item.get("type") == "text":
                    try:
                        return json.loads(item["text"])
                    except:
                        pass
        # Maybe it's the direct result
        if "factSheets" in result:
            return result["factSheets"]
    return None


def main():
    print("=" * 60)
    print("OrgType Fix — Direct MCP Connection")
    print(f"Server: {MCP_BASE}")
    print("=" * 60)

    # Step 1: Get all factsheets
    print("\n[1] Getting all factsheets...")
    result = mcp_call_tool("GetAllFactSheets", {})
    
    if isinstance(result, dict) and "error" in result:
        print(f"  ERROR: {result['error']}")
        sys.exit(1)

    factsheets = extract_factsheets(result)
    if factsheets is None:
        print(f"  Could not extract factsheets from result:")
        print(f"  {json.dumps(result, indent=2)[:500]}")
        sys.exit(1)

    print(f"  Total factsheets: {len(factsheets)}")

    # Show sample to understand the structure
    if factsheets:
        print(f"  Sample keys: {list(factsheets[0].keys())[:10]}")

    # Filter to organizations
    orgs = []
    for fs in factsheets:
        fs_type = fs.get("type", "").lower()
        fs_display_type = fs.get("factSheetType", "").lower()
        fs_type_name = fs.get("factSheetTypeName", "").lower()
        if "organization" in fs_type or "organization" in fs_display_type or "organization" in fs_type_name:
            orgs.append(fs)

    print(f"  Organizations found: {len(orgs)}")

    if not orgs:
        # Maybe GetAllFactSheets only returns summaries? Try getting by ID
        print("\n  GetAllFactSheets returned summaries only.")
        print("  Trying different approach — get individual factsheets by type...")
        
        # Get the IDs of organizations from the summary
        org_ids = [fs.get("id") for fs in factsheets if "organization" in fs.get("type", "").lower()]
        if not org_ids:
            print("  No organization IDs found in summary either.")
            print(f"  Sample types: {set(fs.get('type', '?') for fs in factsheets[:20])}")
            sys.exit(1)
        
        print(f"  Found {len(org_ids)} org IDs. Fetching full details...")
        for oid in org_ids[:3]:
            detail = mcp_call_tool("GetFactSheetById", {"id": oid})
            print(f"    {oid}: {json.dumps(detail, indent=2)[:200]}")
        sys.exit(0)

    # Step 2: Build hierarchy
    print("\n[2] Building hierarchy...")
    org_by_id = {}
    for org in orgs:
        oid = org.get("id") or org.get("Id")
        if oid:
            org_by_id[oid] = org

    # Determine levels
    children_map = {}  # parent_id -> [child_ids]
    for org in orgs:
        oid = org.get("id") or org.get("Id")
        children = org.get("hierarchyChildrenIds") or org.get("HierarchyChildrenIds") or []
        for child_id in children:
            children_map.setdefault(oid, []).append(child_id)

    # Find parent for each org
    parent_map = {}  # child_id -> parent_id
    for parent_id, child_ids in children_map.items():
        for child_id in child_ids:
            parent_map[child_id] = parent_id

    def get_level(org_id, depth=0):
        if depth > 10:
            return depth
        pid = parent_map.get(org_id)
        if not pid or pid not in org_by_id:
            return 1  # root = Country
        return 1 + get_level(pid, depth + 1)

    level_to_type = {1: "Country", 2: "Business Unit", 3: "Department", 4: "Team"}

    # Step 3: Calculate updates needed
    print("\n[3] Calculating required updates...")
    updates = []
    for org in orgs:
        oid = org.get("id") or org.get("Id")
        name = org.get("displayName") or org.get("DisplayName") or "?"
        current = org.get("orgType") or org.get("OrgType") or "(null)"
        level = get_level(oid)
        correct = level_to_type.get(level, "Team")

        if current != correct:
            updates.append({
                "id": oid,
                "name": name,
                "current": current,
                "correct": correct,
                "level": level,
            })

    print(f"  Need to update: {len(updates)} out of {len(orgs)} organizations")

    from collections import Counter
    level_counts = Counter(u["level"] for u in updates)
    for lvl in sorted(level_counts):
        print(f"    Level {lvl} ({level_to_type.get(lvl, '?')}): {level_counts[lvl]}")

    if not updates:
        print("  All organizations already have correct OrgType!")
        sys.exit(0)

    # Preview
    print(f"\n  Preview (first 10):")
    for u in updates[:10]:
        print(f"    {u['name']}: '{u['current']}' → '{u['correct']}' (L{u['level']})")

    # Step 4: Apply updates
    print(f"\n[4] Applying {len(updates)} updates...")
    success = 0
    failed = 0

    for i, u in enumerate(updates):
        result = mcp_call_tool("UpdateFactSheet", {
            "id": u["id"],
            "updates": {"OrgType": u["correct"]}
        })

        is_error = isinstance(result, dict) and "error" in result
        if is_error:
            print(f"  ✗ [{i+1}] {u['name']}: {result['error']}")
            failed += 1
        else:
            success += 1
        
        if (i + 1) % 25 == 0 or (i + 1) == len(updates):
            print(f"  Progress: {i+1}/{len(updates)} ({success} ok, {failed} failed)")
        
        time.sleep(0.1)  # rate limit — new SSE session each time

    print(f"\n{'='*60}")
    print(f"DONE: {success} updated, {failed} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
