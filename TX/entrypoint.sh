#!/bin/bash
set -e

# 1. הרמת ה-Monitor (הקובץ monitor.py מקים את senders_pool ומאזין לתיקייה)
python3 -u -m TX.file_monitor.monitor --path /app/watch_dir &
PYTHON_PID=$!

# המתנה עד שקובץ הסוקט נוצר ע"י ה-senders_pool
for i in {1..30}; do
    if [ -S /tmp/file_monitor.sock ]; then
        break
    fi
    sleep 0.2
done

# 2. הרמת ה-Sender עם 4 הארגומנטים: <worker_id> <dest_ip> <udp_port> <uds_path>
./sender_bin 1 172.20.0.20 8001 /tmp/file_monitor.sock &
CPP_PID=$!

wait -n $PYTHON_PID $CPP_PID
