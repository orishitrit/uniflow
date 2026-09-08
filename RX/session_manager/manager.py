from collections import defaultdict
import os
import time
from typing import Dict, List, Set

from RX.session_manager.file_receiver import FileReceiver
import Schemas.chunk_pb2 as pb


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
    self.connected_workers: Set[str] = set()
    os.makedirs(self.output_dir, exist_ok=True)

  def on_frame_received(self, raw_bytes: bytes) -> None:
    if raw_bytes.startswith(b"RX_WORKER:"):
      worker_id_str = raw_bytes.decode("utf-8", errors="ignore")
      self.connected_workers.add(worker_id_str)
      print(f"[SessionManager] Worker connected: {worker_id_str}")
      return

    packet = pb.PacketMessage()
    try:
      packet.ParseFromString(raw_bytes)
    except Exception as e:
      print(f"[SessionManager Error] Failed to parse Protobuf packet: {e}")
      return

    payload_type = packet.WhichOneof("payload")

    if payload_type == "metadata":
      meta = packet.metadata
      file_id = meta.file_id

      if file_id in self.completed_files or file_id in self.active_sessions:
        return

      print(
          f"[SessionManager] New file session started: {file_id} | Total"
          f" chunks expected: {meta.total_chunks}"
      )
      receiver = FileReceiver(meta, self.output_dir)
      self.active_sessions[file_id] = receiver
      self.session_timestamps[file_id] = time.time()

      if file_id in self.pending_chunks:
        self.pending_timestamps.pop(file_id, None)
        buffered = self.pending_chunks.pop(file_id)
        print(
            f"[SessionManager] Replaying {len(buffered)} buffered chunks for"
            f" {file_id}"
        )
        for buffered_chunk in buffered:
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
          print(
              f"[SessionManager] Buffering out-of-order chunk"
              f" {chunk.chunk_index} for file {file_id}"
          )
          self.pending_chunks[file_id].append(chunk)
          self.pending_timestamps[file_id] = time.time()
        return

      receiver = self.active_sessions[file_id]
      self.session_timestamps[file_id] = time.time()
      receiver.add_chunk(chunk)
      print(
          f"[SessionManager] Received chunk {chunk.chunk_index} for file"
          f" {file_id}"
      )

      if receiver.is_complete_or_recoverable():
        self._finalize_and_close(file_id, receiver)

  def _finalize_and_close(self, file_id: str, receiver: FileReceiver) -> None:
    self.active_sessions.pop(file_id, None)
    self.session_timestamps.pop(file_id, None)

    success = receiver.finalize()
    if success:
      self.completed_files.add(file_id)
      print(
          f"[SessionManager SUCCESS] File {file_id} successfully reconstructed"
          f" and saved to {self.output_dir}!"
      )
    else:
      print(f"[SessionManager Error] Failed to finalize file {file_id}")

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
        print(
            f"[SessionManager Warning] Session {fid} timed out and cleaned up."
        )
        receiver._cleanup(success=False)

    stale_pending = [
        fid
        for fid, last_active in self.pending_timestamps.items()
        if now - last_active > self.timeout_seconds
    ]
    for fid in stale_pending:
      print(f"[SessionManager Warning] Pending chunks for {fid} timed out.")
      self.pending_chunks.pop(fid, None)
      self.pending_timestamps.pop(fid, None)