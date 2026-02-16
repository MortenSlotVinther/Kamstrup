#!/usr/bin/env python3
"""Test MCP using http.client for better streaming control."""
import http.client
import json
import threading
import time
import uuid

API_KEY = "UvaWbr1OUc5T36OAR7YooMwc0J3BMaRUzk0zLE5gSWo="
HOST = "localhost"
PORT = 5000

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
    conn = http.client.HTTPConnection(HOST, PORT, timeout=30)
    headers = {
        "Accept": "text/event-stream",
        "User-Agent": "Debug/1.0",
        "X-API-Key": API_KEY,
    }
    conn.request("GET", "/mcp/sse", headers=headers)
    resp = conn.getresponse()
    print(f"[SSE] Status: {resp.status}")
    
    current_event = None
    while True:
        line = resp.readline()
        if not line:
            print("[SSE] EOF")
            break
        line = line.decode('utf-8').rstrip('\r\n')
        if not line:
            continue
        print(f"[SSE] {line}")
        
        if line.startswith('event:'):
            current_event = line[6:].strip()
        elif line.startswith('data:'):
            data_str = line[5:].strip()
            if current_event == 'endpoint' or (session_url is None and 'sessionId=' in data_str):
                session_url = f"http://{HOST}:{PORT}{data_str}" if data_str.startswith('/') else data_str
                print(f"[SSE] Session URL: {session_url}")
            else:
                try:
                    data = json.loads(data_str)
                    if isinstance(data, dict) and data.get("id") == request_id:
                        response_data = data
                        print(f"[SSE] Got response: {json.dumps(data)[:300]}")
                        return
                except json.JSONDecodeError:
                    pass
            current_event = None

t = threading.Thread(target=sse_reader, daemon=True)
t.start()

# Wait for session
for _ in range(100):
    if session_url:
        break
    time.sleep(0.05)

if not session_url:
    print("FAIL: No session URL")
    exit(1)

# Small delay to ensure SSE is fully established
time.sleep(0.3)

# POST
print(f"\n[POST] Sending to {session_url}")
conn2 = http.client.HTTPConnection(HOST, PORT, timeout=10)
body = json.dumps(payload).encode('utf-8')
conn2.request("POST", session_url.replace(f"http://{HOST}:{PORT}", ""), body=body, headers={
    "Content-Type": "application/json",
    "User-Agent": "Debug/1.0",
    "X-API-Key": API_KEY,
})
resp2 = conn2.getresponse()
print(f"[POST] Status: {resp2.status}")
post_body = resp2.read().decode('utf-8')
print(f"[POST] Body: {post_body[:500]}")

# Wait for SSE response
print("\n[WAIT] Waiting for SSE...")
for _ in range(200):
    if response_data:
        print(f"\n[RESULT] {json.dumps(response_data, indent=2)[:1000]}")
        break
    time.sleep(0.05)
else:
    print("\n[TIMEOUT]")

print("Done")
