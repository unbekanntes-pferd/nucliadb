# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: nucliadb_protos/nodesidecar.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from nucliadb_protos import noderesources_pb2 as nucliadb__protos_dot_noderesources__pb2
try:
  nucliadb__protos_dot_utils__pb2 = nucliadb__protos_dot_noderesources__pb2.nucliadb__protos_dot_utils__pb2
except AttributeError:
  nucliadb__protos_dot_utils__pb2 = nucliadb__protos_dot_noderesources__pb2.nucliadb_protos.utils_pb2

from nucliadb_protos.noderesources_pb2 import *

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!nucliadb_protos/nodesidecar.proto\x12\x0bnodesidecar\x1a#nucliadb_protos/noderesources.proto\"0\n\x07\x43ounter\x12\x11\n\tresources\x18\x01 \x01(\x04\x12\x12\n\nparagraphs\x18\x02 \x01(\x04\"M\n\x13ShadowShardResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12%\n\x05shard\x18\x02 \x01(\x0b\x32\x16.noderesources.ShardId2\xee\x01\n\x0bNodeSidecar\x12:\n\x08GetCount\x12\x16.noderesources.ShardId\x1a\x14.nodesidecar.Counter\"\x00\x12R\n\x11\x43reateShadowShard\x12\x19.noderesources.EmptyQuery\x1a .nodesidecar.ShadowShardResponse\"\x00\x12O\n\x11\x44\x65leteShadowShard\x12\x16.noderesources.ShardId\x1a .nodesidecar.ShadowShardResponse\"\x00P\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'nucliadb_protos.nodesidecar_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _COUNTER._serialized_start=87
  _COUNTER._serialized_end=135
  _SHADOWSHARDRESPONSE._serialized_start=137
  _SHADOWSHARDRESPONSE._serialized_end=214
  _NODESIDECAR._serialized_start=217
  _NODESIDECAR._serialized_end=455
# @@protoc_insertion_point(module_scope)
