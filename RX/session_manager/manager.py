from collections import defaultdict
import os
import time
from typing import Dict, List, Set

import Schemas.chunk_pb2 as pb
from RX.session_manager.file_receiver import FileReceiver


class SessionManager:
    def __init__(
        self,
        output_dir: str,
        timeout_seconds: float = 10.0,
        max_pending_per_file: int = 200,
    ):
        self.output_dir = output_dir
        self.timeout_seconds = timeout_seconds
        self.max_pending_per_file = max_pending_per_file

        self.active_sessions: Dict[str, FileReceiver] = {}
        self.session_timestamps: Dict[str, float] = {}

        self.pending_chunks: Dict[str, List[pb.FileChunk]] = defaultdict(list)
        self.pending_timestamps: Dict[str, float] = {}

        self.completed_files: Set[str] = set()
        os.makedirs(self.output_dir, exist_ok=True)

    def on_frame_received(self, raw_bytes: bytes) -> None:
        packet = pb.PacketMessage()
        packet.ParseFromString(raw_bytes)
        payload_type = packet.WhichOneof("payload")

        if payload_type == "metadata":
            meta = packet.metadata
            file_id = meta.file_id

            if file_id in self.completed_files or file_id in self.active_sessions:
                return

            receiver = FileReceiver(meta, self.output_dir)
            self.active_sessions[file_id] = receiver
            self.session_timestamps[file_id] = time.time()

            if file_id in self.pending_chunks:
                self.pending_timestamps.pop(file_id, None)
                for buffered_chunk in self.pending_chunks.pop(file_id):
                    receiver.add_chunk(buffered_chunk)

            if receiver.is_complete_or_recoverable():
                self._finalize_and_close(file_id, receiver)

        elif payload_type == "chunk":
            chunk = packet.chunk
            file_id = chunk.file_id

            if file_id in self.completed_files:
                return

            if file_id not in self.active_sessions:
                if len(self.pending_chunks[file_id]) < self.max_pending_per_file:
                    self.pending_chunks[file_id].append(chunk)
                    self.pending_timestamps[file_id] = time.time()
                return

            receiver = self.active_sessions[file_id]
            self.session_timestamps[file_id] = time.time()
            receiver.add_chunk(chunk)

            if receiver.is_complete_or_recoverable():
                self._finalize_and_close(file_id, receiver)

    def _finalize_and_close(self, file_id: str, receiver: FileReceiver) -> None:
        self.active_sessions.pop(file_id, None)
        self.session_timestamps.pop(file_id, None)

        success = receiver.finalize()
        if success:
            self.completed_files.add(file_id)

    def cleanup_stale_sessions(self) -> None:
        now = time.time()

        stale_sessions = [
            fid
            for fid, last_active in self.session_timestamps.items()
            if now - last_active > self.timeout_seconds
        ]
        for fid in stale_sessions:
            receiver = self.active_sessions.pop(fid, None)
            self.session_timestamps.pop(fid, None)
            if receiver:
                receiver._cleanup(success=False)

        stale_pending = [
            fid
            for fid, last_active in self.pending_timestamps.items()
            if now - last_active > self.timeout_seconds
        ]
        for fid in stale_pending:
            self.pending_chunks.pop(fid, None)
            self.pending_timestamps.pop(fid, None)