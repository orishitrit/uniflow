import socket, zlib, struct, time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
target = ('127.0.0.1', 8001)

# 1. שליחת פקטה תקינה (Good Packet)
payload1 = b'Hello Uniflow RX Node!'
crc1 = zlib.crc32(payload1) & 0xffffffff
packet1 = struct.pack('!I', crc1) + payload1
sock.sendto(packet1, target)
print('[Sender Test] Sent GOOD packet with valid CRC32.')

time.sleep(1)

# 2. שליחת פקטה משובשת (Bad Packet - Corrupted Payload / Wrong CRC)
payload2 = b'Corrupted Data Packet'
bad_crc = 0xDEADBEEF  # CRC שגוי בכוונה
packet2 = struct.pack('!I', bad_crc) + payload2
sock.sendto(packet2, target)
print('[Sender Test] Sent BAD packet with invalid CRC32.')

time.sleep(1)

# 3. שליחת עוד פקטה תקינה
payload3 = b'Final Successful Test Chunk'
crc3 = zlib.crc32(payload3) & 0xffffffff
packet3 = struct.pack('!I', crc3) + payload3
sock.sendto(packet3, target)
print('[Sender Test] Sent GOOD packet #2.')