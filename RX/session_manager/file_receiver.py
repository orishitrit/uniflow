import hashlib
import math
import os
from typing import Dict, List, Set

import Schemas.chunk_pb2 as pb
import zfec


class FileReceiver:
    def __init__(self, metadata: pb.FileMetadata, output_dir: str):
        self.metadata = metadata
        self.output_dir = output_dir
        self.output_path = os.path.join(output_dir, metadata.file_name)
        self.file_handle = open(self.output_path, "wb+")

        k = self.metadata.total_data_chunks
        if k == 0 or self.metadata.file_size == 0:
            self.chunk_size = 0
        else:
            self.chunk_size = math.ceil(self.metadata.file_size / k)

        self.received_data_indices: Set[int] = set()
        self.parity_chunks: Dict[int, bytes] = {}

    def __del__(self):
        if hasattr(self, "file_handle") and self.file_handle:
            try:
                self.file_handle.close()
            except Exception:
                pass

    def add_chunk(self, chunk: pb.FileChunk) -> None:
        if self.chunk_size == 0:
            return

        if len(chunk.payload) != self.chunk_size:
            return

        if chunk.chunk_type == pb.ChunkType.DATA:
            if chunk.chunk_id in self.received_data_indices:
                return

            self.received_data_indices.add(chunk.chunk_id)
            offset = chunk.chunk_id * self.chunk_size
            self.file_handle.seek(offset)
            self.file_handle.write(chunk.payload)
            self.file_handle.flush()
        else:
            self.parity_chunks[chunk.chunk_id] = chunk.payload

    def is_complete_or_recoverable(self) -> bool:
        k = self.metadata.total_data_chunks
        if k == 0 or self.metadata.file_size == 0:
            return True
        return len(self.received_data_indices) + len(self.parity_chunks) >= k

    def finalize(self) -> bool:
        k = self.metadata.total_data_chunks
        m = self.metadata.total_parity_chunks

        if not self.is_complete_or_recoverable():
            self._cleanup(success=False)
            return False

        try:
            if k > 0 and len(self.received_data_indices) < k:
                self._recover_missing_data(k, m)

            self.file_handle.truncate(self.metadata.file_size)
            self.file_handle.flush()

            is_valid = self._verify_hash()
            self._cleanup(success=is_valid)
            return is_valid

        except Exception:
            self._cleanup(success=False)
            return False

    def _recover_missing_data(self, k: int, m: int) -> None:
        decoder = zfec.Decoder(k, k + m)
        chunks_for_decoding: List[bytes] = []
        indices_for_decoding: List[int] = []

        for chunk_id in sorted(self.received_data_indices):
            if len(indices_for_decoding) == k:
                break
            offset = chunk_id * self.chunk_size
            self.file_handle.seek(offset)
            data = self.file_handle.read(self.chunk_size)
            chunks_for_decoding.append(data)
            indices_for_decoding.append(chunk_id)

        for chunk_id in sorted(self.parity_chunks.keys()):
            if len(indices_for_decoding) == k:
                break
            chunks_for_decoding.append(self.parity_chunks[chunk_id])
            indices_for_decoding.append(chunk_id)

        missing_indices = [idx for idx in range(k) if idx not in self.received_data_indices]
        recovered_blocks = decoder.decode(chunks_for_decoding, indices_for_decoding)

        for missing_idx, data in zip(missing_indices, recovered_blocks):
            offset = missing_idx * self.chunk_size
            self.file_handle.seek(offset)
            self.file_handle.write(data)
            self.received_data_indices.add(missing_idx)
        self.file_handle.flush()

    def _verify_hash(self) -> bool:
        self.file_handle.seek(0)
        hasher = hashlib.sha256()

        while chunk := self.file_handle.read(65536):
            hasher.update(chunk)

        calculated = hasher.hexdigest().lower()
        expected = self.metadata.sha256_hash.lower()
        return calculated == expected

    def _cleanup(self, success: bool) -> None:
        if self.file_handle:
            try:
                self.file_handle.close()
            except Exception:
                pass
            self.file_handle = None

        self.parity_chunks.clear()
        self.received_data_indices.clear()

        if not success and os.path.exists(self.output_path):
            try:
                os.remove(self.output_path)
            except OSError:
                pass