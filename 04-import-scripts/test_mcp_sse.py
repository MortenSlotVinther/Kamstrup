#!/usr/bin/env python3
"""Debug MCP SSE connection."""
import json
import threading
import time
import uuid
from urllib.request import urlopen, Request

MCP_BASE = "http://localhost:5000"
API_KEY = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="

request_id = str(uuid.uuid4())
payload = {
    "jsonrpc": "2.0",
    "id": request_id,
    "method": "tools/list",
}

session_url = None
response_data = None
error_msg = None

def sse_thread_fn():
    global session_url, response_data, error_msg
    try:
        headers = {
            "Accept": "text/event-stream",
            "User-Agent": "Debug/1.0",
            "X-API-Key": API_KEY,
        }
        req = Request(MCP_BASE + "/mcp/sse", headers=headers, method="GET")
        print("[SSE] Opening connection...")
        resp = urlopen(req, timeout=30)
        print(f"[SSE] Connected. Status: {resp.status}")
        
        current_event = None
        for raw_line in resp:
            line = raw_line.decode('utf-8').rstrip('\r\n')
            if not line:
                continue
            print(f"[SSE] Line: {line}")
            
            if line.startswith('event:'):
                current_event = line[6:].strip()
            elif line.startswith('data:'):
                data_str = line[5:].strip()
                if current_event == 'endpoint' or (session_url is None and 'sessionId=' in data_str):
                    if data_str.startswith('/'):
                        session_url = MCP_BASE + data_str
                    else:
                        session_url = data_str
                    print(f"[SSE] Got session URL: {session_url}")
                else:
                    try:
                        data = json.loads(data_str)
                        print(f"[SSE] Got JSON: {json.dumps(data)[:200]}")
                        if isinstance(data, dict) and data.get("id") == request_id:
                            response_data = data
                            print("[SSE] Got our response!")
                            return
                    except json.JSONDecodeError:
                        pass
                current_event = None
        print("[SSE] Stream ended")
    except Exception as e:
        error_msg = str(e)
        print(f"[SSE] Error: {e}")

# Start SSE reader
t = threading.Thread(target=sse_thread_fn, daemon=True)
t.start()

# Wait for session URL
for _ in range(50):
    if session_url:
        break
    time.sleep(0.1)

if not session_url:
    print("FAIL: No session URL received")
    exit(1)

print(f"\n[POST] Sending to {session_url}")
time.sleep(0.5)  # Give SSE a moment to stabilize

try:
    post_headers = {
        "Content-Type": "application/json",
        "User-Agent": "Debug/1.0",
        "X-API-Key": API_KEY,
    }
    req = Request(
        session_url,
        data=json.dumps(payload).encode('utf-8'),
        headers=post_headers,
        method="POST"
    )
    with urlopen(req, timeout=10) as r:
        body = r.read().decode('utf-8')
        print(f"[POST] Status: {r.status}")
        print(f"[POST] Body: {body[:500]}")
except Exception as e:
    print(f"[POST] Error: {e}")
    import traceback
    traceback.print_exc()

# Wait for SSE response
print("\n[WAIT] Waiting for SSE response...")
for _ in range(100):
    if response_data:
        print(f"\n[RESULT] {json.dumps(response_data, indent=2)[:500]}")
        break
    if error_msg:
        print(f"\n[ERROR] {error_msg}")
        break
    time.sleep(0.1)
else:
    print("\n[TIMEOUT] No response received")

print("\nDone")
