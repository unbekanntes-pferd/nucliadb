# Copyright (C) 2021 Bosutech XXI S.L.
#
# nucliadb is offered under the AGPL v3.0 and as commercial software.
# For commercial licensing, contact us at info@nuclia.com.
#
# AGPL:
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncIterator

from nucliadb_protos.nodereader_pb2 import (
    DocumentItem,
    EdgeList,
    GetShardRequest,
    ParagraphItem,
    ParagraphSearchRequest,
    ParagraphSearchResponse,
    RelationSearchRequest,
    RelationSearchResponse,
    SearchRequest,
    SearchResponse,
    StreamRequest,
    SuggestRequest,
    SuggestResponse,
    TypeList,
)
from nucliadb_protos.noderesources_pb2 import EmptyQuery, Resource, ResourceID
from nucliadb_protos.noderesources_pb2 import Shard as NodeResourcesShard
from nucliadb_protos.noderesources_pb2 import (
    ShardCleaned,
    ShardCreated,
    ShardId,
    ShardIds,
    ShardMetadata,
    VectorSetID,
    VectorSetList,
)
from nucliadb_protos.nodewriter_pb2 import OpStatus, SetGraph

from nucliadb.ingest.settings import settings

try:
    from nucliadb_node_binding import NodeReader  # type: ignore
    from nucliadb_node_binding import NodeWriter  # type: ignore
except ImportError:  # pragma: no cover
    NodeReader = None
    NodeWriter = None


class LocalReaderWrapper:
    reader: NodeReader

    def __init__(self):
        self.reader = NodeReader.new()
        self.executor = ThreadPoolExecutor(settings.local_reader_threads)

    async def Search(self, request: SearchRequest) -> SearchResponse:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.executor, self.reader.search, request.SerializeToString()
        )
        pb_bytes = bytes(result)
        pb = SearchResponse()
        pb.ParseFromString(pb_bytes)
        return pb

    async def ParagraphSearch(
        self, request: ParagraphSearchRequest
    ) -> ParagraphSearchResponse:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.executor, self.reader.paragraph_search, request.SerializeToString()
        )
        pb_bytes = bytes(result)
        pb = ParagraphSearchResponse()
        pb.ParseFromString(pb_bytes)
        return pb

    async def RelationSearch(
        self, request: RelationSearchRequest
    ) -> RelationSearchResponse:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.executor, self.reader.relation_search, request.SerializeToString()
        )
        pb_bytes = bytes(result)
        pb = RelationSearchResponse()
        pb.ParseFromString(pb_bytes)
        return pb

    async def GetShard(self, request: GetShardRequest) -> NodeResourcesShard:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.executor, self.reader.get_shard, request.SerializeToString()
        )
        pb_bytes = bytes(result)
        shard = NodeResourcesShard()
        shard.ParseFromString(pb_bytes)
        return shard

    async def Suggest(self, request: SuggestRequest) -> SuggestResponse:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.executor, self.reader.suggest, request.SerializeToString()
        )
        pb_bytes = bytes(result)
        pb = SuggestResponse()
        pb.ParseFromString(pb_bytes)
        return pb

    async def Documents(
        self, stream_request: StreamRequest
    ) -> AsyncIterator[DocumentItem]:
        loop = asyncio.get_running_loop()
        q: asyncio.Queue[DocumentItem] = asyncio.Queue(1)
        exception = None
        _END = object()

        def thread_generator():
            nonlocal exception
            generator = self.reader.documents(stream_request.SerializeToString())
            try:
                element = generator.next()
                while element is not None:
                    pb_bytes = bytes(element)
                    pb = DocumentItem()
                    pb.ParseFromString(pb_bytes)
                    asyncio.run_coroutine_threadsafe(q.put(pb), loop).result()
                    element = generator.next()
            except TypeError:
                # this is the end
                pass
            except Exception as e:
                exception = e
            finally:
                asyncio.run_coroutine_threadsafe(q.put(_END), loop).result()

        t1 = threading.Thread(target=thread_generator)
        t1.start()

        while True:
            next_item = await q.get()
            if next_item is _END:
                break
            yield next_item
        if exception is not None:
            raise exception
        await loop.run_in_executor(self.executor, t1.join)

    async def Paragraphs(
        self, stream_request: StreamRequest
    ) -> AsyncIterator[ParagraphItem]:
        loop = asyncio.get_running_loop()
        q: asyncio.Queue[ParagraphItem] = asyncio.Queue(1)
        exception = None
        _END = object()

        def thread_generator():
            nonlocal exception
            generator = self.reader.paragraphs(stream_request.SerializeToString())
            try:
                element = generator.next()
                while element is not None:
                    pb_bytes = bytes(element)
                    pb = ParagraphItem()
                    pb.ParseFromString(pb_bytes)
                    asyncio.run_coroutine_threadsafe(q.put(pb), loop).result()
                    element = generator.next()
            except TypeError:
                # this is the end
                pass
            except Exception as e:
                exception = e
            finally:
                asyncio.run_coroutine_threadsafe(q.put(_END), loop).result()

        t1 = threading.Thread(target=thread_generator)
        t1.start()
        while True:
            next_item = await q.get()
            if next_item is _END:
                break
            yield next_item
        if exception is not None:
            raise exception
        await loop.run_in_executor(self.executor, t1.join)

    async def RelationEdges(self, request: ShardId):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.executor, self.reader.relation_edges, request.SerializeToString()
        )
        pb_bytes = bytes(result)
        edge_list = EdgeList()
        edge_list.ParseFromString(pb_bytes)
        return edge_list

    async def RelationTypes(self, request: ShardId):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.executor, self.reader.relation_types, request.SerializeToString()
        )
        pb_bytes = bytes(result)
        type_list = TypeList()
        type_list.ParseFromString(pb_bytes)
        return type_list


class LocalWriterWrapper:
    writer: NodeWriter

    def __init__(self):
        self.writer = NodeWriter.new()
        self.executor = ThreadPoolExecutor(settings.local_reader_threads)

    async def GetShard(self, request: ShardId) -> ShardId:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.executor, self.writer.get_shard, request.SerializeToString()
        )
        pb_bytes = bytes(result)
        pb = ShardId()
        pb.ParseFromString(pb_bytes)
        return pb

    async def NewShard(self, request: ShardMetadata) -> ShardCreated:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.new_shard, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        shard_created = ShardCreated()
        shard_created.ParseFromString(pb_bytes)
        return shard_created

    async def DeleteShard(self, request: ShardId) -> ShardId:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.delete_shard, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        shard_id = ShardId()
        shard_id.ParseFromString(pb_bytes)
        return shard_id

    async def ListShards(self, request: EmptyQuery) -> ShardIds:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.list_shards, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        shard_ids = ShardIds()
        shard_ids.ParseFromString(pb_bytes)
        return shard_ids

    async def CleanAndUpgradeShard(self, request: ShardId) -> ShardCleaned:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor,
            self.writer.clean_and_upgrade_shard,
            request.SerializeToString(),
        )
        pb_bytes = bytes(resp)
        resp = ShardCleaned()
        resp.ParseFromString(pb_bytes)
        return resp

    async def RemoveVectorSet(self, request: VectorSetID):
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.del_vectorset, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        resp = OpStatus()
        resp.ParseFromString(pb_bytes)
        return resp

    async def AddVectorSet(self, request: VectorSetID):
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.set_vectorset, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        resp = OpStatus()
        resp.ParseFromString(pb_bytes)
        return resp

    async def ListVectorSets(self, request: ShardId):
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.get_vectorset, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        resp = VectorSetList()
        resp.ParseFromString(pb_bytes)
        return resp

    async def SetResource(self, request: Resource) -> OpStatus:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.set_resource, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        op_status = OpStatus()
        op_status.ParseFromString(pb_bytes)
        return op_status

    async def RemoveResource(self, request: ResourceID) -> OpStatus:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.remove_resource, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        op_status = OpStatus()
        op_status.ParseFromString(pb_bytes)
        return op_status

    async def JoinGraph(self, request: SetGraph) -> OpStatus:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(
            self.executor, self.writer.join_graph, request.SerializeToString()
        )
        pb_bytes = bytes(resp)
        op_status = OpStatus()
        op_status.ParseFromString(pb_bytes)
        return op_status
