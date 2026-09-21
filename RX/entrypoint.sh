#!/bin/bash
set -e

# 1. הרמת Session Manager
python3 -u -m RX.session_manager.main &
PYTHON_PID=$!

sleep 1

# 2. הרמת 3 תהליכי Receiver עבור 3 הערוצים (Worker IDs 1, 2, 3)
# ארגומנטים: <worker_id> <listen_port> <uds_path>
PIDS=()

for i in {1..3}; do
    PORT=$((9000 + i)) # יפיק 9001, 9002, 9003
    ./receiver_bin $i $PORT /tmp/uniflow_rx_master.sock &
    PIDS+=($!)
done

# המתנה לסיום של תהליך הפייתון או של אחד ה-Receivers
wait -n $PYTHON_PID "${PIDS[@]}"