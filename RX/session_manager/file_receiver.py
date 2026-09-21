import hashlib
import os
import traceback
from typing import Dict, Set

import Schemas.chunk_pb2 as pb


class FileReceiver:
    def __init__(self, metadata: pb.FileMetadata, output_dir: str):
        self.metadata = metadata
        self.output_dir = output_dir
        self.output_path = os.path.join(output_dir, metadata.file_name)

        self.data_chunks: Dict[int, bytes] = {}
        self.parity_chunks: Dict[int, bytes] = {}

    def add_chunk(self, chunk: pb.FileChunk) -> None:
        if chunk.chunk_type == pb.ChunkType.DATA:
            if chunk.chunk_id not in self.data_chunks:
                self.data_chunks[chunk.chunk_id] = chunk.payload
        else:
            if chunk.chunk_id not in self.parity_chunks:
                self.parity_chunks[chunk.chunk_id] = chunk.payload

    def is_complete(self) -> bool:
        """מחזיר True ברגע שהצטברו k מקטעי Data. מתעלם מחורים באינדקסים."""
        k = self.metadata.total_data_chunks
        if self.metadata.file_size == 0:
            return True
        if k == 0:
            return False
        # התיקון: בדיקת כמות בלבד, ללא בדיקת רציפות מספרית
        return len(self.data_chunks) >= k

    def finalize(self) -> bool:
        k = self.metadata.total_data_chunks

        if not self.is_complete():
            print(f"[FileReceiver] Finalize failed: Only {len(self.data_chunks)}/{k} chunks received.")
            self._cleanup(success=False)
            return False

        try:
            print(f"[FileReceiver] Assembling {k} chunks sequentially (ignoring Parity ID gaps)...")
            hasher = hashlib.sha256()

            with open(self.output_path, "wb") as f:
                bytes_written = 0
                target_size = self.metadata.file_size

                # התיקון הקריטי: מיון המזהים שהתקבלו בפועל וכתיבתם ברצף
                sorted_data_ids = sorted(self.data_chunks.keys())

                # לוקחים בדיוק k מקטעי Data ראשונים וכותבים אותם
                for chunk_id in sorted_data_ids[:k]:
                    payload = self.data_chunks[chunk_id]
                    
                    remaining = target_size - bytes_written
                    if remaining <= 0:
                        break

                    # חיתוך ה-payload האחרון אם יש בו ריפוד (padding)
                    chunk_to_write = payload[:remaining] if len(payload) > remaining else payload
                    
                    f.write(chunk_to_write)
                    hasher.update(chunk_to_write)
                    bytes_written += len(chunk_to_write)

                f.flush()

            calculated = hasher.hexdigest().lower()
            expected = self.metadata.sha256_hash.lower()

            print(f"[FileReceiver Hash] Calculated: {calculated}")
            print(f"[FileReceiver Hash] Expected:   {expected}")

            is_valid = (calculated == expected)
            if not is_valid:
                print(f"[FileReceiver Error] Hash mismatch! Verification failed.")

            self._cleanup(success=is_valid)
            return is_valid

        except Exception as e:
            print(f"[FileReceiver Error] Exception during finalize: {e}")
            traceback.print_exc()
            self._cleanup(success=False)
            return False

    def _cleanup(self, success: bool) -> None:
        self.data_chunks.clear()
        self.parity_chunks.clear()

        if not success and os.path.exists(self.output_path):
            try:
                os.remove(self.output_path)
            except OSError:
                pass