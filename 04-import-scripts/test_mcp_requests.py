#!/usr/bin/env python3
"""Test MCP using requests library with streaming."""
import requests
import json
import threading
import time
import uuid

API_KEY = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="
BASE = "http://localhost:5000"

request_id = str(uuid.uuid4())
payload = {
    "jsonrpc": "2.0",
    "id": request_id,
    "method": "tools/list",
}

session_url = None
response_data = None

def sse_reader():
    global session_url, response_data
    try:
        r = requests.get(
            f"{BASE}/mcp/sse",
            headers={"Accept": "text/event-stream", "X-API-Key": API_KEY},
            stream=True,
            timeout=30,
        )
        print(f"[SSE] Status: {r.status_code}")
        print(f"[SSE] Headers: {dict(r.headers)}")
        
        current_event = None
        for line in r.iter_lines(decode_unicode=True):
            if line is None:
                continue
            print(f"[SSE] {line}")
            
            if line.startswith('event:'):
                current_event = line[6:].strip()
            elif line.startswith('data:'):
                data_str = line[5:].strip()
                if current_event == 'endpoint' or (session_url is None and 'sessionId=' in data_str):
                    session_url = f"{BASE}{data_str}" if data_str.startswith('/') else data_str
                    print(f"[SSE] ✓ Session URL: {session_url}")
                else:
                    try:
                        data = json.loads(data_str)
                        if isinstance(data, dict) and data.get("id") == request_id:
                            response_data = data
                            print(f"[SSE] ✓ Got response!")
                            return
                    except json.JSONDecodeError:
                        pass
                current_event = None
            elif line == '':
                pass  # empty line separator
        
        print("[SSE] Stream ended")
    except Exception as e:
        print(f"[SSE] Error: {e}")

t = threading.Thread(target=sse_reader, daemon=True)
t.start()

# Wait for session URL
for i in range(100):
    if session_url:
        break
    time.sleep(0.05)

if not session_url:
    print("FAIL: No session URL")
    exit(1)

time.sleep(0.3)

# POST
print(f"\n[POST] {session_url}")
r2 = requests.post(
    session_url,
    json=payload,
    headers={"X-API-Key": API_KEY},
    timeout=10,
)
print(f"[POST] Status: {r2.status_code}")
print(f"[POST] Body: {r2.text[:500]}")

# Wait
print("\n[WAIT]...")
for i in range(200):
    if response_data:
        print(f"\n[OK] {json.dumps(response_data, indent=2)[:1000]}")
        break
    time.sleep(0.05)
else:
    print("[TIMEOUT]")

print("Done")
