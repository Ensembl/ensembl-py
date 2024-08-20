# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit testing of `ensembl.xrefs.xref_update_db_model` module."""


import pytest

from ensembl.xrefs.xref_update_db_model import Base
from ensembl.utils.database import UnitTestDB


@pytest.mark.parametrize("test_dbs", [[{"src": "core_db"}]], indirect=True)
class TestCoreModels:
    """Tests the `~ensembl.xrefs.xref_update_db_model` ORMs"""

    dbc: UnitTestDB = None

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, test_dbs: dict[str, UnitTestDB]) -> None:
        """Loads the required fixtures and values as class attributes.

        Args:
            test_dbs: Generator of unit test databases (fixture).
        """
        type(self).dbc = test_dbs["core_db"].dbc

    def test_create_db(self) -> None:
        """Test the creation of a database with the xref_update models schema."""
        self.dbc.create_all_tables(Base.metadata)
        assert set(self.dbc.tables.keys()) == set(Base.metadata.tables.keys())
