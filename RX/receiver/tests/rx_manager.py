import socket
import os
import struct

UDS_PATH = "/tmp/uniflow_rx_master.sock"

# ניקוי סוקט ישן אם קיים
if os.path.exists(UDS_PATH):
    os.remove(UDS_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(UDS_PATH)
server.listen(1)

print(f"[Mock Manager] Listening on UDS: {UDS_PATH}")

conn, _ = server.accept()
print("[Mock Manager] RX Worker connected!")

# 1. קריאת הודעת הזדהות ראשונית
ident = conn.recv(1024).decode('utf-8', errors='ignore')
print(f"[Mock Manager] Received Identity: '{ident}'")

# 2. לולאת קליטת פקטות Payload
print("[Mock Manager] Ready to receive clean payloads...\n" + "-"*40)
try:
    while True:
        # קריאת 4 בייטים של אורך
        header = conn.recv(4)
        if not header or len(header) < 4:
            print("[Mock Manager] Connection closed by Receiver.")
            break
        
        payload_len = struct.unpack("!I", header)[0]
        
        # קריאת ה-Payload עצמו לפי האורך
        payload = b""
        while len(payload) < payload_len:
            chunk = conn.recv(payload_len - len(payload))
            if not chunk:
                break
            payload += chunk
            
        print(f"[Mock Manager] Received Payload ({len(payload)} bytes): {payload.decode('utf-8', errors='ignore')}")
except KeyboardInterrupt:
    print("\n[Mock Manager] Shutting down.")
finally:
    conn.close()
    server.close()
    if os.path.exists(UDS_PATH):
        os.remove(UDS_PATH)