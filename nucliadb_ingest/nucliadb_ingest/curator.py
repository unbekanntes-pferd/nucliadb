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
import logging
import os
import sys
import time
from functools import lru_cache
from typing import Dict, Generator, List, Optional, Tuple

import aiofiles
import nats
from nats import errors
from nats.aio.client import Client, Msg
from nats.aio.subscription import Subscription
from nats.js.client import JetStreamContext
from nucliadb_protos.audit_pb2 import AuditRequest
from nucliadb_protos.knowledgebox_pb2 import EntitiesGroup
from nucliadb_protos.resources_pb2 import FieldComputedMetadata, FieldID
from nucliadb_protos.writer_pb2 import GetEntitiesResponse
from sentry_sdk import capture_exception

from nucliadb_ingest.fields.base import FIELD_METADATA
from nucliadb_ingest.maindb.driver import Driver
from nucliadb_ingest.orm.processor import Processor
from nucliadb_ingest.orm.resource import KB_REVERSE_REVERSE
from nucliadb_ingest.sentry import SENTRY, set_sentry
from nucliadb_ingest.utils import get_driver
from nucliadb_utils.settings import audit_settings, running_settings
from nucliadb_utils.storages.storage import Storage, StorageField
from nucliadb_utils.utilities import get_cache, get_storage

CACHE_FOLDER = "/cache/{worker}"
CURATOR_ID = "/internal/curator/{worker}"

logger = logging.getLogger("nucliadb_ingest")


class Entities:

    data: Optional[GetEntitiesResponse] = None

    def __init__(self, cache: str, kbid: str):
        self.cache = cache
        self.kbid = kbid

    async def save(self):
        if self.data is None:
            raise AttributeError("No data")
        async with aiofiles.open(f"{self.cache}/{self.kbid}", "wb+") as f:
            await f.write(self.data.SerializeToString())

    async def load(self):
        async with aiofiles.open(f"{self.cache}/{self.kbid}", "rb+") as f:
            self.data = GetEntitiesResponse()
            self.data.kb = self.kbid
            self.data.ParseFromString(await f.read())

    def merge(self, resource_ners: List[Dict[str, str]]):
        if self.data is None:
            raise AttributeError("No data")
        for resource_ner in resource_ners:
            for ner, ner_type in resource_ner.items():
                if ner not in self.data.groups[ner_type].entities:
                    self.data.groups[ner_type].entities[ner].value = ner

    def items(
        self,
    ) -> Generator[Tuple[Optional[str], Optional[EntitiesGroup]], None, None]:
        if self.data is None:
            yield None, None
        else:
            for key, value in self.data.groups.items():
                yield key, value


class Consumer:
    nc: Optional[Client] = None
    js: Optional[JetStreamContext] = None
    subscription: Optional[Subscription] = None

    def __init__(
        self,
        partition: int,
        driver: Driver,
        storage: Storage,
        js: JetStreamContext,
        ttl: int = 30 * 60,
    ):
        self.partition = partition
        self.driver = driver
        self.storage = storage
        self.cache = os.environ.get("CACHE_FOLDER", CACHE_FOLDER).format(
            worker=self.partition
        )
        self.dead_time = time.time() + ttl
        self.kbs_touch: List[str] = []
        self.lock = asyncio.Lock()
        self.js = js
        os.makedirs(self.cache, exist_ok=True)

    async def initialize(self):

        last_curator_key = CURATOR_ID.format(worker=self.partition)
        txn = await self.driver.begin()
        last_curator_seq = await txn.get(last_curator_key)
        await txn.abort()
        if last_curator_seq is None:
            last_curator_seq = 1

        target = audit_settings.audit_jetstream_target.format(
            partition=self.partition, type=AuditRequest.MODIFIED
        )

        self.subscription = await self.js.subscribe(
            subject=target,
            stream=audit_settings.audit_stream,
            flow_control=True,
            config=nats.js.api.ConsumerConfig(
                deliver_policy=nats.js.api.DeliverPolicy.BY_START_SEQUENCE,
                opt_start_seq=last_curator_seq,
                ack_policy=nats.js.api.AckPolicy.EXPLICIT,
                max_ack_pending=1,
                max_deliver=10000,
                ack_wait=10,
                idle_heartbeat=5.0,
            ),
        )
        logger.info(f"Subscription created to {target}")

    async def finalize(self):
        await self.subscription.unsubscribe()

    async def loop(self):
        seq = None
        try:
            while time.time() < self.dead_time:
                msg = await self.subscription.next_msg(timeout=0.5)
                seq = await self.subscription_worker(msg)
        except errors.TimeoutError:
            pass

        if seq is not None:
            last_curator_key = CURATOR_ID.format(worker=self.partition)
            txn = await self.driver.begin()
            await txn.set(last_curator_key, f"{seq}".encode())
            await txn.commit(resource=False)

        kbs = set(self.kbs_touch)
        if len(kbs) > 0:
            cache = await get_cache()
            self.proc = Processor(driver=self.driver, storage=self.storage, cache=cache)
            await self.proc.initialize()

            for kbid in kbs:
                entities = await self.get_knowledgebox_entities(kbid)
                txn = await self.driver.begin()
                kbobj = await self.proc.get_kb_obj(txn, kbid)
                if kbobj is not None:
                    for group, entities in entities.items():
                        await kbobj.set_entities(group, entities)
                await txn.commit(resource=False)

    async def subscription_worker(self, msg: Msg) -> int:
        subject = msg.subject
        reply = msg.reply
        seqid = int(msg.reply.split(".")[5])
        logger.debug(
            f"Message received: subject:{subject}, seqid: {seqid}, reply: {reply}"
        )

        async with self.lock:
            try:
                pb = AuditRequest()
                pb.ParseFromString(msg.data)

                kb_entities = await self.get_knowledgebox_entities(pb.kbid)
                for field in pb.field_metadata:
                    resource_entities = await self.get_resource_entities(
                        pb.kbid, pb.rid, field
                    )

                    kb_entities.merge(resource_entities)

                self.kbs_touch.append(pb.kbid)
                await kb_entities.save()

            except Exception as e:
                # Unhandled exceptions that need to be retried after a small delay
                if SENTRY:
                    capture_exception(e)

                logger.info(f"Check sentry for more details: {str(e)}")
                raise e
            else:
                # Successful processing
                await msg.ack()
        return seqid

    async def get_resource_entities(
        self, kbid: str, rid: str, field: FieldID
    ) -> List[Dict[str, str]]:
        type_char = KB_REVERSE_REVERSE[field.field_type]
        sf: StorageField = self.storage.file_extracted(
            kbid, rid, type_char, field.field, FIELD_METADATA
        )
        payload = await self.storage.download_pb(sf, FieldComputedMetadata)

        entities = []

        entities.append(payload.metadata.ner)
        for split_metadata in payload.split_metadata.values():
            entities.append(split_metadata.ner)
        return entities

    @lru_cache(maxsize=200)
    async def get_knowledgebox_entities(self, kbid: str) -> Entities:
        entities_pb = Entities(self.cache, kbid)
        await entities_pb.load()
        return entities_pb


class Nats:
    async def disconnected_cb(self):
        logger.info("Got disconnected from NATS!")

    async def reconnected_cb(self):
        # See who we are connected to on reconnect.
        logger.info(
            "Got reconnected to NATS {url}".format(url=self.nc.connected_url.netloc)
        )

    async def error_cb(self, e):
        logger.error("There was an error on consumer ingest worker: {}".format(e))

    async def closed_cb(self):
        logger.info("Connection is closed on NATS")

    async def initialize(self):

        options = {
            "error_cb": self.error_cb,
            "closed_cb": self.closed_cb,
            "reconnected_cb": self.reconnected_cb,
        }

        if audit_settings.audit_jetstream_auth is not None:
            options["user_credentials"] = audit_settings.audit_jetstream_auth

        if len(audit_settings.audit_jetstream_servers) > 0:
            options["servers"] = audit_settings.audit_jetstream_servers

        try:
            self.nc = await nats.connect(**options)
        except Exception:
            pass

        self.js = self.nc.jetstream()

    async def finalize(self):
        try:
            await self.nc.drain()
        except RuntimeError:
            pass
        except nats.errors.ConnectionClosedError:
            pass

        try:
            await self.nc.close()
        except RuntimeError:
            pass
        except AttributeError:
            pass


async def main():
    consumers: List[Consumer] = []
    driver = await get_driver()
    storage = await get_storage()

    logger.info("STARTING CURATOR")
    nc = Nats()
    await nc.initialize()
    for partition in range(audit_settings.audit_partitions):
        consumer = Consumer(partition, driver, storage, nc.js)
        await consumer.initialize()
        consumers.append(consumer)

    await asyncio.gather([consumer.loop() for consumer in consumers])

    for consumer in consumers:
        await consumer.finalize()
    await nc.finalize()

    logger.info("END CURATOR KB")


def run() -> int:
    if running_settings.sentry_url and SENTRY:
        set_sentry(
            running_settings.sentry_url,
            running_settings.running_environment,
            running_settings.logging_integration,
        )

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s.%(msecs)02d] [%(levelname)s] - %(name)s - %(message)s",
        stream=sys.stderr,
    )

    return asyncio.run(main())
