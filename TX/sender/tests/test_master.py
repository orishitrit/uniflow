import socket
import os
import struct
import time

UDS_PATH = "/tmp/uniflow_tx_master.sock"

if os.path.exists(UDS_PATH):
    os.remove(UDS_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(UDS_PATH)
server.listen(1)

print("[Master] Waiting for Sender to connect...")
conn, _ = server.accept()
print("[Master] Sender connected!")

# 1. קריאת ההרשמה
raw_len = conn.recv(4)
if raw_len:
    msg_len = struct.unpack("!I", raw_len)[0]
    reg_msg = conn.recv(msg_len).decode()
    print(f"[Master] Received registration: {reg_msg}")

# 2. שליחת הפיילוט
payload = b"Hello"
header = struct.pack("!I", len(payload))

print("[Master] Sending payload: 'Hello'")
conn.sendall(header + payload)

# 3. נותנים ל-Sender זמן לעבד ולשדר ב-UDP לפני שמנתקים
print("[Master] Payload sent! Keeping UDS open...")
time.sleep(10)

conn.close()
server.close()