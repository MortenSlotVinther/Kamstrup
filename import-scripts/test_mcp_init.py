#!/usr/bin/env python3
"""Test MCP with proper initialization handshake."""
import requests
import json
import threading
import time
import uuid
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

API_KEY = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="
BASE = "http://localhost:5000"

session_url = None
responses = []

def sse_reader():
    global session_url
    try:
        r = requests.get(
            f"{BASE}/mcp/sse",
            headers={"Accept": "text/event-stream", "X-API-Key": API_KEY},
            stream=True,
            timeout=60,
        )
        print(f"[SSE] Status: {r.status_code}")
        
        current_event = None
        for line in r.iter_lines(decode_unicode=True):
            if line is None:
                continue
            if not line:
                continue
            # print(f"[SSE] {line}")
            
            if line.startswith('event:'):
                current_event = line[6:].strip()
            elif line.startswith('data:'):
                data_str = line[5:].strip()
                if current_event == 'endpoint' or (session_url is None and 'sessionId=' in data_str):
                    session_url = f"{BASE}{data_str}" if data_str.startswith('/') else data_str
                    print(f"[SSE] Session: {session_url}")
                else:
                    try:
                        data = json.loads(data_str)
                        responses.append(data)
                        print(f"[SSE] Response: {json.dumps(data)[:200]}")
                    except json.JSONDecodeError:
                        print(f"[SSE] Non-JSON data: {data_str[:100]}")
                current_event = None
        
        print("[SSE] Stream ended")
    except Exception as e:
        print(f"[SSE] Error: {type(e).__name__}: {e}")

t = threading.Thread(target=sse_reader, daemon=True)
t.start()

for i in range(100):
    if session_url:
        break
    time.sleep(0.05)

if not session_url:
    print("FAIL: No session URL after 5s")
    exit(1)

time.sleep(0.3)

# Step 1: Send initialize request first
init_id = str(uuid.uuid4())
init_payload = {
    "jsonrpc": "2.0",
    "id": init_id,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {
            "name": "OrgTypeFix",
            "version": "1.0"
        }
    }
}

print(f"\n[1] Sending initialize...")
r = requests.post(session_url, json=init_payload, headers={"X-API-Key": API_KEY}, timeout=10)
print(f"    Status: {r.status_code}, Body: {r.text[:200]}")

time.sleep(0.5)

# Check for response on SSE
print(f"    SSE responses so far: {len(responses)}")

# Step 2: Send initialized notification
notif_payload = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
}
print(f"\n[2] Sending initialized notification...")
r = requests.post(session_url, json=notif_payload, headers={"X-API-Key": API_KEY}, timeout=10)
print(f"    Status: {r.status_code}, Body: {r.text[:200]}")

time.sleep(0.5)

# Step 3: Now try tools/list
list_id = str(uuid.uuid4())
list_payload = {
    "jsonrpc": "2.0",
    "id": list_id,
    "method": "tools/list",
}
print(f"\n[3] Sending tools/list...")
r = requests.post(session_url, json=list_payload, headers={"X-API-Key": API_KEY}, timeout=10)
print(f"    Status: {r.status_code}, Body: {r.text[:500]}")

time.sleep(1)

# Check SSE responses
print(f"\n[RESULT] Total SSE responses: {len(responses)}")
for resp in responses:
    rid = resp.get("id", "?")
    if "result" in resp:
        result = resp["result"]
        if "tools" in result:
            tools = result["tools"]
            print(f"  tools/list: {len(tools)} tools")
            for tool in tools[:5]:
                print(f"    - {tool.get('name')}")
        elif "serverInfo" in result:
            print(f"  initialize: {result['serverInfo']}")
        else:
            print(f"  Response {rid}: {json.dumps(result)[:200]}")
    elif "error" in resp:
        print(f"  Error {rid}: {resp['error']}")

print("\nDone")
