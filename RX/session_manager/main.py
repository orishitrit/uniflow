import os
import sys

from RX.session_manager.file_receiver import FileReceiver
from RX.session_manager.ipc_server import IPCServer
from RX.session_manager.manager import SessionManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

RECEIVED_FILES_DIR = os.path.join(PROJECT_ROOT, "received_files")
os.makedirs(RECEIVED_FILES_DIR, exist_ok=True)

SOCKET_PATH = "/tmp/uniflow_rx_master.sock"


def run():
    server = IPCServer(socket_paths=[SOCKET_PATH])
    manager = SessionManager(output_dir=RECEIVED_FILES_DIR, timeout_seconds=10.0)

    server.register_observer(manager.on_frame_received)
    server.register_tick_handler(manager.cleanup_stale_sessions)

    try:
        server.start()
    except KeyboardInterrupt:
        server.close_all()
        sys.exit(0)


if __name__ == "__main__":
    run()