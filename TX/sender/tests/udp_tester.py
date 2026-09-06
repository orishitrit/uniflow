import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"[UDP Listener] Listening on {UDP_IP}:{UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"\n[UDP Listener] Received {len(data)} bytes from {addr}:")
    print(f"  Hex:  {data.hex(' ')}")
    print(f"  Text: {data[4:]} (Payload after 4-byte CRC32)")