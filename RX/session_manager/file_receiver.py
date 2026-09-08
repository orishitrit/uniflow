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
        self.chunk_size: int = math.ceil(self.metadata.file_size / k)
        self.received_data_indices: Set[int] = set()
        self.parity_chunks: Dict[int, bytes] = {}

    def __del__(self):
        if hasattr(self, "file_handle") and self.file_handle:
            try:
                self.file_handle.close()
            except Exception:
                pass

    def add_chunk(self, chunk: pb.FileChunk) -> None:
        if len(chunk.payload) != self.chunk_size:
            return

        if chunk.chunk_type == pb.ChunkType.DATA:
            if chunk.chunk_id in self.received_data_indices:
                return

            self.received_data_indices.add(chunk.chunk_id)
            offset = chunk.chunk_id * self.chunk_size
            self.file_handle.seek(offset)
            self.file_handle.write(chunk.payload)
        else:
            self.parity_chunks[chunk.chunk_id] = chunk.payload

    def is_complete_or_recoverable(self) -> bool:
        k = self.metadata.total_data_chunks
        return len(self.received_data_indices) + len(self.parity_chunks) >= k

    def finalize(self) -> bool:
        k = self.metadata.total_data_chunks
        m = self.metadata.total_parity_chunks

        if not self.is_complete_or_recoverable():
            self._cleanup(success=False)
            return False

        try:
            if len(self.received_data_indices) < k:
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

        for chunk_id in self.received_data_indices:
            if len(indices_for_decoding) == k:
                break
            offset = chunk_id * self.chunk_size
            self.file_handle.seek(offset)
            data = self.file_handle.read(self.chunk_size)

            if len(data) < self.chunk_size:
                data = data.ljust(self.chunk_size, b"\x00")

            chunks_for_decoding.append(data)
            indices_for_decoding.append(chunk_id)

        for chunk_id, parity_data in self.parity_chunks.items():
            if len(indices_for_decoding) == k:
                break
            chunks_for_decoding.append(parity_data)
            indices_for_decoding.append(chunk_id)

        recovered_blocks = decoder.decode(chunks_for_decoding, indices_for_decoding)

        for chunk_id in range(k):
            if chunk_id not in self.received_data_indices:
                missing_data = recovered_blocks[chunk_id]
                offset = chunk_id * self.chunk_size
                self.file_handle.seek(offset)
                self.file_handle.write(missing_data)
                self.received_data_indices.add(chunk_id)

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