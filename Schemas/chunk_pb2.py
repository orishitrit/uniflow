"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    7,
    35,
    1,
    '',
    'Schemas/chunk.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13Schemas/chunk.proto\x12\x07uniflow\"\x92\x01\n\x0c\x46ileMetadata\x12\x0f\n\x07\x66ile_id\x18\x01 \x01(\t\x12\x11\n\tfile_name\x18\x02 \x01(\t\x12\x11\n\tfile_size\x18\x03 \x01(\x04\x12\x19\n\x11total_data_chunks\x18\x04 \x01(\r\x12\x1b\n\x13total_parity_chunks\x18\x05 \x01(\r\x12\x13\n\x0bsha256_hash\x18\x06 \x01(\t\"g\n\tFileChunk\x12\x0f\n\x07\x66ile_id\x18\x01 \x01(\t\x12\x10\n\x08\x63hunk_id\x18\x02 \x01(\r\x12&\n\nchunk_type\x18\x03 \x01(\x0e\x32\x12.uniflow.ChunkType\x12\x0f\n\x07payload\x18\x04 \x01(\x0c\"j\n\rPacketMessage\x12)\n\x08metadata\x18\x01 \x01(\x0b\x32\x15.uniflow.FileMetadataH\x00\x12#\n\x05\x63hunk\x18\x02 \x01(\x0b\x32\x12.uniflow.FileChunkH\x00\x42\t\n\x07payload*!\n\tChunkType\x12\x08\n\x04\x44\x41TA\x10\x00\x12\n\n\x06PARITY\x10\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Schemas.chunk_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CHUNKTYPE']._serialized_start=394
  _globals['_CHUNKTYPE']._serialized_end=427
  _globals['_FILEMETADATA']._serialized_start=33
  _globals['_FILEMETADATA']._serialized_end=179
  _globals['_FILECHUNK']._serialized_start=181
  _globals['_FILECHUNK']._serialized_end=284
  _globals['_PACKETMESSAGE']._serialized_start=286
  _globals['_PACKETMESSAGE']._serialized_end=392
# @@protoc_insertion_point(module_scope)
