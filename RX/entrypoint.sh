#!/bin/bash
set -e

# 1. הרמת Session Manager
python3 -u -m RX.session_manager.main &
PYTHON_PID=$!

sleep 1

# 2. הרמת ה-Receiver עם 3 הארגומנטים: <worker_id> <listen_port> <uds_path>
./receiver_bin 1 9001 /tmp/uniflow_rx_master.sock &
CPP_PID=$!

wait -n $PYTHON_PID $CPP_PID
