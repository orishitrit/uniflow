import math
from typing import Dict, List
import Schemas.chunk_pb2 as pb
import zfec


def calculate_total_parity_chunks(
    total_data_chunks: int, ratio: float = 0.3
) -> int:
  if total_data_chunks <= 0:
    return 0
  return max(1, math.ceil(total_data_chunks * ratio))


def create_single_parity_chunk(
    chunks_data: List[bytes],
    file_id: str,
    parity_index: int,
    total_data_chunks: int,
    total_parity_chunks: int,
) -> pb.FileChunk:
  k = total_data_chunks
  m = total_parity_chunks

  if k <= 0 or m <= 0:
    raise ValueError("k and m must be positive integers.")

  if k + m > 256:
    raise ValueError(f"Total chunks (k + m = {k + m}) exceeds zfec limit of 256")

  if not (0 <= parity_index < m):
    raise IndexError(
        f"parity_index {parity_index} out of range (0 <= idx < {m})"
    )

  if len(chunks_data) != k:
    raise ValueError(f"Expected {k} data chunks, received {len(chunks_data)}")

  max_len = max(len(c) for c in chunks_data)
  padded_chunks = [c.ljust(max_len, b"\x00") for c in chunks_data]

  encoder = zfec.Encoder(k, k + m)
  global_chunk_id = k + parity_index

  encoded_blocks = encoder.encode(padded_chunks)
  parity_payload = encoded_blocks[global_chunk_id]

  parity_chunk = pb.FileChunk()
  parity_chunk.file_id = file_id
  parity_chunk.chunk_id = global_chunk_id
  parity_chunk.chunk_type = pb.ChunkType.PARITY
  parity_chunk.payload = parity_payload

  return parity_chunk


def decode_chunks(
    available_chunks: Dict[int, bytes], k_data: int, m_parity: int
) -> List[bytes]:
  if len(available_chunks) < k_data:
    raise ValueError(
        f"Need at least {k_data} chunks, got {len(available_chunks)}"
    )

  if all(i in available_chunks for i in range(k_data)):
    return [available_chunks[i] for i in range(k_data)]

  sorted_indexes = sorted(available_chunks.keys())[:k_data]

  max_len = max(len(available_chunks[i]) for i in sorted_indexes)
  data_list = [
      available_chunks[i].ljust(max_len, b"\x00") for i in sorted_indexes
  ]

  decoder = zfec.Decoder(k_data, k_data + m_parity)
  return decoder.decode(data_list, sorted_indexes)