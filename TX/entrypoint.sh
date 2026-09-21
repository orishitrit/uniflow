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

# 2. הרמת 3 תהליכי Sender עבור 3 הערוצים (Worker IDs 1, 2, 3)
# ארגומנטים: <worker_id> <dest_ip> <udp_port> <uds_path>
PIDS=()

for i in {1..3}; do
    PORT=$((8000 + i)) # יפיק 8001, 8002, 8003
    ./sender_bin $i 172.20.0.20 $PORT /tmp/file_monitor.sock &
    PIDS+=($!)
done

# המתנה לסיום של תהליך הפייתון או של אחד ה-Senders
wait -n $PYTHON_PID "${PIDS[@]}"