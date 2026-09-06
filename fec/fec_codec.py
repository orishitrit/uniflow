import math
from typing import List, Dict
import zfec

def calculate_total_parity_chunks(total_data_chunks: int, ratio: float = 0.3) -> int:
    if total_data_chunks <= 0:
        return 0
    return max(1, math.ceil(total_data_chunks * ratio))

def create_parity_chunks(chunks: List[bytes], m_parity: int) -> List[bytes]:
    k = len(chunks)
    if k == 0 or m_parity <= 0:
        return []
    encoder = zfec.Encoder(k, k + m_parity)
    return encoder.encode(chunks)[k:]

def decode_chunks(available_chunks: Dict[int, bytes], k_data: int, m_parity: int) -> List[bytes]:
    if len(available_chunks) < k_data:
        raise ValueError(f"Need at least {k_data} chunks, got {len(available_chunks)}")
    if all(i in available_chunks for i in range(k_data)):
        return [available_chunks[i] for i in range(k_data)]
    
    indexes = list(available_chunks.keys())[:k_data]
    data = [available_chunks[i] for i in indexes]
    return zfec.Decoder(k_data, k_data + m_parity).decode(data, indexes)

