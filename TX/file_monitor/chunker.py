from Schemas import chunk_pb2
from TX.file_monitor.chunk_dispatcher import send
import hashlib

def chunk_id_gen():
    id = 0
    while True:
        yield id
        id += 1

def chunk_file(file_path, chunk_id_generator, chunk_size = 1024):
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk_builder(chunk, 1, next(chunk_id_generator))
    #להוסיף לוגיקת יתירות

def chunk_builder(chunk, chunk_type, chunk_id):
    file_chunk = chunk_pb2.FileChunk()
    file_chunk.file_id = 2
    file_chunk.chunk_id = chunk_id
    file_chunk.chunk_type = chunk_type
    file_chunk.payload = chunk
    return file_chunk

def metadata_chunk_builder(file_path):
    metadata_chunk = chunk_pb2.FileMetadata()
    metadata_chunk.file_name = file_path.name
    metadata_chunk.file_size = file_path.stat().st_size
    metadata_chunk.hash = hash_file(file_path)
    metadata_chunk.file_id = metadata_chunk.hash.hexdigest()[:8]
    metadata_chunk.total_data_chunks = (metadata_chunk.file_size // 1024) + 1
    metadata_chunk.total_parity_chunks = 0  # Placeholder for parity chunks

    return metadata_chunk

def hash_file(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def file_chunking(file_path):
    chunk_id_generator = chunk_id_gen()
    meta_data = metadata_chunk_builder(file_path)
    yield meta_data

    for chunk in chunk_file(file_path, chunk_id_generator):
        processed_chunk = chunk_builder(chunk, chunk_type="data")
        processed_chunk.file_id = meta_data.file_id
        yield processed_chunk

    print(f"File chunking completed for: {file_path.name}")

