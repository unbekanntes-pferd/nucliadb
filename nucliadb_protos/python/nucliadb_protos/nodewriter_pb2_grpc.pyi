"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import abc
import grpc
import nucliadb_protos.noderesources_pb2
import nucliadb_protos.nodewriter_pb2
from nucliadb_protos.noderesources_pb2 import (
    EmptyQuery as EmptyQuery,
    EmptyResponse as EmptyResponse,
    IndexMetadata as IndexMetadata,
    IndexParagraph as IndexParagraph,
    IndexParagraphs as IndexParagraphs,
    ParagraphMetadata as ParagraphMetadata,
    ParagraphPosition as ParagraphPosition,
    Resource as Resource,
    ResourceID as ResourceID,
    Shard as Shard,
    ShardCleaned as ShardCleaned,
    ShardCreated as ShardCreated,
    ShardId as ShardId,
    ShardIds as ShardIds,
    ShardList as ShardList,
    ShardMetadata as ShardMetadata,
    TextInformation as TextInformation,
    VectorSentence as VectorSentence,
    VectorSetID as VectorSetID,
    VectorSetList as VectorSetList,
)

class NodeWriterStub:
    def __init__(self, channel: grpc.Channel) -> None: ...
    GetShard: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ShardId,
        nucliadb_protos.noderesources_pb2.ShardId,
    ]
    NewShard: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ShardMetadata,
        nucliadb_protos.noderesources_pb2.ShardCreated,
    ]
    CleanAndUpgradeShard: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ShardId,
        nucliadb_protos.noderesources_pb2.ShardCleaned,
    ]
    DeleteShard: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ShardId,
        nucliadb_protos.noderesources_pb2.ShardId,
    ]
    ListShards: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.EmptyQuery,
        nucliadb_protos.noderesources_pb2.ShardIds,
    ]
    GC: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ShardId,
        nucliadb_protos.noderesources_pb2.EmptyResponse,
    ]
    SetResource: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.Resource,
        nucliadb_protos.nodewriter_pb2.OpStatus,
    ]
    DeleteRelationNodes: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.nodewriter_pb2.DeleteGraphNodes,
        nucliadb_protos.nodewriter_pb2.OpStatus,
    ]
    JoinGraph: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.nodewriter_pb2.SetGraph,
        nucliadb_protos.nodewriter_pb2.OpStatus,
    ]
    RemoveResource: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ResourceID,
        nucliadb_protos.nodewriter_pb2.OpStatus,
    ]
    AddVectorSet: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.VectorSetID,
        nucliadb_protos.nodewriter_pb2.OpStatus,
    ]
    RemoveVectorSet: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.VectorSetID,
        nucliadb_protos.nodewriter_pb2.OpStatus,
    ]
    ListVectorSets: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ShardId,
        nucliadb_protos.noderesources_pb2.VectorSetList,
    ]
    MoveShard: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.nodewriter_pb2.MoveShardRequest,
        nucliadb_protos.noderesources_pb2.EmptyResponse,
    ]
    AcceptShard: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.nodewriter_pb2.AcceptShardRequest,
        nucliadb_protos.noderesources_pb2.EmptyResponse,
    ]

class NodeWriterServicer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def GetShard(
        self,
        request: nucliadb_protos.noderesources_pb2.ShardId,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.ShardId: ...
    @abc.abstractmethod
    def NewShard(
        self,
        request: nucliadb_protos.noderesources_pb2.ShardMetadata,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.ShardCreated: ...
    @abc.abstractmethod
    def CleanAndUpgradeShard(
        self,
        request: nucliadb_protos.noderesources_pb2.ShardId,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.ShardCleaned: ...
    @abc.abstractmethod
    def DeleteShard(
        self,
        request: nucliadb_protos.noderesources_pb2.ShardId,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.ShardId: ...
    @abc.abstractmethod
    def ListShards(
        self,
        request: nucliadb_protos.noderesources_pb2.EmptyQuery,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.ShardIds: ...
    @abc.abstractmethod
    def GC(
        self,
        request: nucliadb_protos.noderesources_pb2.ShardId,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.EmptyResponse: ...
    @abc.abstractmethod
    def SetResource(
        self,
        request: nucliadb_protos.noderesources_pb2.Resource,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.OpStatus: ...
    @abc.abstractmethod
    def DeleteRelationNodes(
        self,
        request: nucliadb_protos.nodewriter_pb2.DeleteGraphNodes,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.OpStatus: ...
    @abc.abstractmethod
    def JoinGraph(
        self,
        request: nucliadb_protos.nodewriter_pb2.SetGraph,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.OpStatus: ...
    @abc.abstractmethod
    def RemoveResource(
        self,
        request: nucliadb_protos.noderesources_pb2.ResourceID,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.OpStatus: ...
    @abc.abstractmethod
    def AddVectorSet(
        self,
        request: nucliadb_protos.noderesources_pb2.VectorSetID,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.OpStatus: ...
    @abc.abstractmethod
    def RemoveVectorSet(
        self,
        request: nucliadb_protos.noderesources_pb2.VectorSetID,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.OpStatus: ...
    @abc.abstractmethod
    def ListVectorSets(
        self,
        request: nucliadb_protos.noderesources_pb2.ShardId,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.VectorSetList: ...
    @abc.abstractmethod
    def MoveShard(
        self,
        request: nucliadb_protos.nodewriter_pb2.MoveShardRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.EmptyResponse: ...
    @abc.abstractmethod
    def AcceptShard(
        self,
        request: nucliadb_protos.nodewriter_pb2.AcceptShardRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.noderesources_pb2.EmptyResponse: ...

def add_NodeWriterServicer_to_server(servicer: NodeWriterServicer, server: grpc.Server) -> None: ...

class NodeSidecarStub:
    def __init__(self, channel: grpc.Channel) -> None: ...
    GetCount: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ShardId,
        nucliadb_protos.nodewriter_pb2.Counter,
    ]
    CreateShadowShard: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.EmptyQuery,
        nucliadb_protos.nodewriter_pb2.ShadowShardResponse,
    ]
    DeleteShadowShard: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.noderesources_pb2.ShardId,
        nucliadb_protos.nodewriter_pb2.ShadowShardResponse,
    ]

class NodeSidecarServicer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def GetCount(
        self,
        request: nucliadb_protos.noderesources_pb2.ShardId,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.Counter: ...
    @abc.abstractmethod
    def CreateShadowShard(
        self,
        request: nucliadb_protos.noderesources_pb2.EmptyQuery,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.ShadowShardResponse: ...
    @abc.abstractmethod
    def DeleteShadowShard(
        self,
        request: nucliadb_protos.noderesources_pb2.ShardId,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.nodewriter_pb2.ShadowShardResponse: ...

def add_NodeSidecarServicer_to_server(servicer: NodeSidecarServicer, server: grpc.Server) -> None: ...
