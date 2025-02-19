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

import tempfile

import pyarrow as pa  # type: ignore
from nucliadb_protos.dataset_pb2 import TaskType, TrainSet

from nucliadb_dataset.dataset import NucliaDBDataset, download_all_partitions
from nucliadb_sdk.entities import Entity
from nucliadb_sdk.knowledgebox import KnowledgeBox


def test_datascientist_tokens(knowledgebox: KnowledgeBox, temp_folder):
    knowledgebox.upload(
        text="I'm Ramon",
        entities=[Entity(type="NAME", value="Ramon", positions=[(5, 9)])],
    )

    knowledgebox.upload(
        text="I'm not Ramon",
        entities=[Entity(type="NAME", value="Ramon", positions=[(8, 13)])],
    )

    knowledgebox.upload(
        text="I'm Aleix",
        entities=[Entity(type="NAME", value="Aleix", positions=[(5, 9)])],
    )

    arrow_filenames = download_all_partitions(
        task="TOKEN_CLASSIFICATION",
        knowledgebox=knowledgebox,
        path=temp_folder,
    )

    for filename in arrow_filenames:
        with pa.memory_map(filename, "rb") as source:
            loaded_array = pa.ipc.open_stream(source).read_all()
            assert len(loaded_array) == 3


def test_live_token_classification(
    knowledgebox: KnowledgeBox, upload_data_token_classification
):
    trainset = TrainSet()
    trainset.type = TaskType.TOKEN_CLASSIFICATION
    trainset.filter.labels.append("PERSON")
    trainset.batch_size = 2

    with tempfile.TemporaryDirectory() as tmpdirname:
        fse = NucliaDBDataset(
            client=knowledgebox.client,
            trainset=trainset,
            base_path=tmpdirname,
        )
        partitions = fse.get_partitions()
        assert len(partitions) == 1
        filename = fse.read_partition(partitions[0])

        with pa.memory_map(filename, "rb") as source:
            loaded_array = pa.ipc.open_stream(source).read_all()
            assert len(loaded_array) == 2
