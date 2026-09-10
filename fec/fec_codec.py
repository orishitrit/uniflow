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
    chunk_id: int,
) -> pb.FileChunk:
    k = len(chunks_data)
    if k <= 0:
        raise ValueError("chunks_data cannot be empty.")
    if k + 1 > 256:
        raise ValueError(f"Block size ({k}) exceeds zfec limit.")

    # ריפוד כל הצ'אנקים לאותו אורך בדיוק
    max_len = max(len(c) for c in chunks_data)
    padded_chunks = [c.ljust(max_len, b"\x00") for c in chunks_data]

    # k בלוקי מידע -> סה"כ k + 1 בלוקים (כלומר בדיוק בלוק יתירות אחד נוסף)
    encoder = zfec.Encoder(k, k + 1)

    # מקבלים רשימה עם איבר אחד בלבד [0]
    parity_payload = encoder.encode(padded_chunks)[0]

    parity_chunk = pb.FileChunk()
    parity_chunk.file_id = str(file_id)
    parity_chunk.chunk_id = chunk_id
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