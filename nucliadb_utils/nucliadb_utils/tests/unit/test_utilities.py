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

from unittest.mock import AsyncMock, patch

import pytest

from nucliadb_utils import utilities


@pytest.fixture(autouse=True)
def reset_main():
    utilities.MAIN.clear()


def test_clean_utility():
    utilities.set_utility(utilities.Utility.CACHE, "test")
    assert utilities.get_utility(utilities.Utility.CACHE) == "test"
    utilities.clean_utility(utilities.Utility.CACHE)
    assert utilities.get_utility(utilities.Utility.CACHE) is None


@pytest.mark.asyncio
async def test_get_storage_s3():
    s3 = AsyncMock()
    with patch.object(utilities.storage_settings, "file_backend", "s3"), patch(
        "nucliadb_utils.storages.s3.S3Storage", return_value=s3
    ):
        assert await utilities.get_storage() == s3


@pytest.mark.asyncio
async def test_get_storage_gcs():
    gcs = AsyncMock()
    with patch.object(utilities.storage_settings, "file_backend", "gcs"), patch(
        "nucliadb_utils.storages.gcs.GCSStorage", return_value=gcs
    ):
        assert await utilities.get_storage() == gcs


@pytest.mark.asyncio
async def test_get_storage_local():
    local = AsyncMock()
    with patch.object(
        utilities.storage_settings, "file_backend", "local"
    ), patch.object(utilities.storage_settings, "local_files", "/files"), patch(
        "nucliadb_utils.storages.local.LocalStorage", return_value=local
    ):
        assert await utilities.get_storage() == local


@pytest.mark.asyncio
async def test_get_storage_missing():
    with patch.object(utilities.storage_settings, "file_backend", "missing"):
        with pytest.raises(AttributeError):
            await utilities.get_storage()


@pytest.mark.asyncio
async def test_get_local_storage():
    assert utilities.get_local_storage() is not None


@pytest.mark.asyncio
async def test_get_nuclia_storage():
    assert await utilities.get_nuclia_storage() is not None


@pytest.mark.asyncio
async def test_get_cache():
    with patch("nucliadb_utils.utilities.Cache", return_value=AsyncMock()):
        assert await utilities.get_cache() is not None


@pytest.mark.asyncio
async def test_get_pubsub():
    with patch("nucliadb_utils.utilities.NatsPubsub", return_value=AsyncMock()):
        assert await utilities.get_pubsub() is not None


@pytest.mark.asyncio
async def test_finalize_utilities():
    util = AsyncMock()
    utilities.MAIN["test"] = util

    await utilities.finalize_utilities()

    util.finalize.assert_called_once()
    assert len(utilities.MAIN) == 0


@pytest.mark.asyncio
async def test_start_audit_utility():
    with patch("nucliadb_utils.utilities.NatsPubsub", return_value=AsyncMock()), patch(
        "nucliadb_utils.utilities.StreamAuditStorage", return_value=AsyncMock()
    ):
        await utilities.start_audit_utility()

        assert "audit" in utilities.MAIN


@pytest.mark.asyncio
async def test_stop_audit_utility():
    with patch("nucliadb_utils.utilities.NatsPubsub", return_value=AsyncMock()), patch(
        "nucliadb_utils.utilities.StreamAuditStorage", return_value=AsyncMock()
    ):
        await utilities.start_audit_utility()
        await utilities.stop_audit_utility()

        assert "audit" not in utilities.MAIN
