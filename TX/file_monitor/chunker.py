from Schemas import chunk_pb2
import hashlib
from pathlib import Path


def chunk_id_gen():
    id = 0
    while True:
        yield id
        id += 1


def chunk_file(file_path, chunk_id_generator, metadata_chunk, chunk_size=1024):
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            yield chunk_builder(chunk, chunk_pb2.DATA, next(chunk_id_generator), metadata_chunk.file_id)
    # להוסיף לוגיקת יתירות


def chunk_builder(chunk, chunk_type, chunk_id, file_id):
    file_chunk = chunk_pb2.FileChunk()
    file_chunk.file_id = str(file_id)
    file_chunk.chunk_id = chunk_id
    file_chunk.chunk_type = chunk_type
    file_chunk.payload = chunk
    return file_chunk


def hash_file(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def metadata_chunk_builder(file_path):
    metadata_chunk = chunk_pb2.FileMetadata()
    metadata_chunk.file_name = file_path.name
    metadata_chunk.file_size = file_path.stat().st_size
    
    file_hash = hash_file(file_path)
    metadata_chunk.sha256_hash = file_hash  # תואם לסכמה
    metadata_chunk.file_id = file_hash[:8]
    metadata_chunk.total_data_chunks = (metadata_chunk.file_size // 1024) + 1
    # metadata_chunk.total_parity_chunks בינתיים ריק/ברירת מחדל

    return metadata_chunk


def file_chunking(file_path):
    chunk_id_generator = chunk_id_gen()
    meta_data = metadata_chunk_builder(file_path)

    for i in range(5):
        yield meta_data

    for chunk in chunk_file(file_path, chunk_id_generator, meta_data):
        yield chunk

    print(f"File chunking completed for: {file_path.name}")