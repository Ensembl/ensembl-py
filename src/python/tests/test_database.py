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
"""Unit testing of :mod:`database` module.

The unit testing is divided into one test class per submodule/class found in this module, and one test method
per public function/class method.

Typical usage example::

    $ pytest test_database.py

"""

from contextlib import nullcontext as does_not_raise
import os
from pathlib import Path
from typing import ContextManager, Dict

import pytest
from pytest import FixtureRequest, param, raises
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.automap import automap_base

from ensembl.database import DBConnection, UnitTestDB


class TestUnitTestDB:
    """Tests :class:`UnitTestDB` class.

    Attributes:
        dbs (dict): Dictionary of :class:`UnitTestDB` objects with the database name as key.

    """

    dbs: Dict[str, UnitTestDB] = {}

    @pytest.mark.parametrize(
        "src, name, expectation",
        [
            (Path("mock_dir"), None, raises(FileNotFoundError)),
            param(
                Path("mock_db"),
                None,
                does_not_raise(),
                marks=pytest.mark.dependency(name="init", scope="class"),
            ),
            param(
                Path("mock_db"),
                "renamed_db",
                does_not_raise(),
                marks=pytest.mark.dependency(name="init_renamed", scope="class"),
            ),
        ],
    )
    def test_init(
        self,
        request: FixtureRequest,
        shared_data_dir: Path,
        src: Path,
        name: str,
        expectation: ContextManager,
    ) -> None:
        """Tests that the object :class:`UnitTestDB` is initialised correctly.

        See :class:`UnitTestDB` for a detailed description of `src` (i.e. `dump_dir`) and `name` parameters.

        Args:
            request: Access to the requesting test context.
            shared_data_dir: Path to the shared test data folder.
            src: Directory path where the test database schema and content files are located. If a relative
                path is provided, the root folder will be ``src/python/tests/databases``.
            name: Name to give to the new database.
            expectation: Context manager for the expected exception, i.e. the test will only pass if that
                exception is raised. Use :class:`~contextlib.nullcontext` if no exception is expected.

        """
        with expectation:
            server_url = request.config.getoption("server")
            src_path = src if src.is_absolute() else shared_data_dir / src
            db_key = name if name else src.name
            self.dbs[db_key] = UnitTestDB(server_url, src_path, name)
            # Check that the database has been created correctly
            assert self.dbs[db_key], "UnitTestDB should not be empty"
            assert self.dbs[db_key].dbc, "UnitTestDB's database connection should not be empty"
            # Check that the database has been loaded correctly from the dump files
            result = self.dbs[db_key].dbc.execute("SELECT * FROM gibberish")
            assert len(result.fetchall()) == 6, "Unexpected number of rows found in 'gibberish' table"

    @pytest.mark.parametrize(
        "db_key",
        [
            param("mock_db", marks=pytest.mark.dependency(depends=["init"], scope="class")),
            param("renamed_db", marks=pytest.mark.dependency(depends=["init_renamed"], scope="class")),
        ],
    )
    def test_drop(self, db_key: str) -> None:
        """Tests that the previously created object :class:`UnitTestDB` is dropped correctly.

        Args:
            db_key: Key assigned to the UnitTestDB created in :meth:`TestUnitTestDB.test_init()`.

        """
        self.dbs[db_key].drop()
        if self.dbs[db_key].dbc.dialect == "sqlite":
            # For SQLite databases, just check if the database file still exists
            assert not Path(self.dbs[db_key].dbc.db_name).exists(), "The database file has not been deleted"
        else:
            with raises(OperationalError, match=r"Unknown database"):
                self.dbs[db_key].dbc.execute("SELECT * FROM gibberish")


@pytest.mark.parametrize("db", [{"src": "mock_db"}], indirect=True)
class TestDBConnection:
    """Tests :class:`DBConnection` class.

    Attributes:
        dbc (DBConnection): Database connection to the unit test database.
        server (str): Server url where the unit test database is hosted.

    """

    dbc: DBConnection = None
    server: str = ""

    # autouse=True makes this fixture be executed before any test_* method of this class, and scope='class' to
    # execute it only once per class parametrization
    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request: FixtureRequest, db: UnitTestDB) -> None:
        """Loads the required fixtures and values as class attributes.

        Args:
            request: Access to the requesting test context.
            db: Unit test database (fixture).

        """
        # Use type(self) instead of self as a workaround to @classmethod decorator (unsupported by pytest and
        # required when scope is set to "class" <https://github.com/pytest-dev/pytest/issues/3778>)
        type(self).dbc = db.dbc
        type(self).server = request.config.getoption("server")

    @pytest.mark.dependency(name="test_init", scope="class")
    def test_init(self) -> None:
        """Tests that the object :class:`DBConnection` is initialised correctly."""
        assert self.dbc, "DBConnection object should not be empty"

    @pytest.mark.dependency(name="test_db_name", depends=["test_init"], scope="class")
    def test_db_name(self) -> None:
        """Tests :meth:`DBConnection.db_name` property."""
        assert self.dbc.db_name == f"{os.environ['USER']}_mock_db"

    @pytest.mark.dependency(depends=["test_init", "test_db_name"], scope="class")
    def test_url(self) -> None:
        """Tests :meth:`DBConnection.url` property."""
        assert self.dbc.url == self.server + self.dbc.db_name

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_host(self) -> None:
        """Tests :meth:`DBConnection.host` property."""
        assert self.dbc.host == make_url(self.server).host

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_dialect(self) -> None:
        """Tests :meth:`DBConnection.dialect` property."""
        assert self.dbc.dialect == make_url(self.server).drivername

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_tables(self) -> None:
        """Tests :meth:`DBConnection.tables` property."""
        tables = {"gibberish", "meta"}
        assert set(self.dbc.tables.keys()) == tables

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_get_primary_key_columns(self) -> None:
        """Tests :meth:`DBConnection.get_primary_key_columns()` method."""
        table = "gibberish"
        assert set(self.dbc.get_primary_key_columns(table)) == {
            "id",
            "grp",
        }, f"Unexpected set of primary key columns found in table '{table}'"

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_get_columns(self) -> None:
        """Tests :meth:`DBConnection.get_columns()` method."""
        table = "gibberish"
        assert set(self.dbc.get_columns(table)) == {
            "id",
            "grp",
            "value",
        }, f"Unexpected set of columns found in table '{table}'"

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_schema_type(self) -> None:
        """Tests :meth:`DBConnection.schema_type` property."""
        assert self.dbc.schema_type == "compara", "Unexpected schema type found in database's 'meta' table"

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_schema_version(self) -> None:
        """Tests :meth:`DBConnection.schema_version` property."""
        assert self.dbc.schema_version == 99, "Unexpected schema version found in database's 'meta' table"

    @pytest.mark.dependency(name="test_connect", depends=["test_init"], scope="class")
    def test_connect(self) -> None:
        """Tests :meth:`DBConnection.connect()` method."""
        connection = self.dbc.connect()
        assert connection, "Connection object should not be empty"
        result = connection.execute("SELECT * FROM meta")
        assert len(result.fetchall()) == 3, "Unexpected number of rows found in 'meta' table"
        connection.close()

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_begin(self) -> None:
        """Tests :meth:`DBConnection.begin()` method."""
        with self.dbc.begin() as connection:
            assert connection, "Connection object should not be empty"
            result = connection.execute("SELECT * FROM gibberish")
            assert len(result.fetchall()) == 6, "Unexpected number of rows found in 'gibberish' table"

    @pytest.mark.dependency(depends=["test_init"], scope="class")
    def test_dispose(self) -> None:
        """Tests :meth:`DBConnection.dispose()` method."""
        self.dbc.dispose()
        # SQLAlchemy uses a "pool-less" connection system for SQLite
        if self.dbc.dialect != "sqlite":
            num_conn = self.dbc._engine.pool.checkedin()  # pylint: disable=protected-access
            assert num_conn == 0, "A new pool should have 0 checked-in connections"

    @pytest.mark.parametrize(
        "query, nrows, expectation",
        [
            param(
                "SELECT * FROM gibberish",
                6,
                does_not_raise(),
                marks=pytest.mark.dependency(name="test_exec1", depends=["test_init"], scope="class"),
            ),
            param(
                "SELECT * FROM my_table",
                0,
                raises(SQLAlchemyError, match=r"(my_table.* doesn't exist|no such table: my_table)"),
                marks=pytest.mark.dependency(name="test_exec2", depends=["test_init"], scope="class"),
            ),
        ],
    )
    def test_execute(self, query: str, nrows: int, expectation: ContextManager) -> None:
        """Tests :meth:`DBConnection.execute()` method.

        Args:
            query: SQL query.
            nrows: Number of rows expected to be returned from the query.
            expectation: Context manager for the expected exception, i.e. the test will only pass if that
                exception is raised. Use :class:`~contextlib.nullcontext` if no exception is expected.

        """
        with expectation:
            result = self.dbc.execute(query)
            assert len(result.fetchall()) == nrows, "Unexpected number of rows returned"

    @pytest.mark.dependency(depends=["test_init", "test_connect", "test_exec1", "test_exec2"], scope="class")
    @pytest.mark.parametrize(
        "identifier, row1, row2, before, after",
        [
            (7, {"grp": "grp4", "value": 1}, {"grp": "grp5", "value": 1}, 0, 2),
            (7, {"grp": "grp6", "value": 1}, {"grp": "grp6", "value": 2}, 2, 2),
        ],
    )
    def test_session_scope(
        self, identifier: int, row1: Dict[str, str], row2: Dict[str, str], before: int, after: int
    ) -> None:
        """Tests :meth:`DBConnection.session_scope()` method.

        Bear in mind that the second parameterization of this test will fail if the dialect/table engine
        does not support rollback transactions.

        Args:
            identifier: ID of the rows to add.
            row1: first row's group and value.
            row2: second row's group and value.
            before: Number of rows in ``gibberish`` for `id` before adding the rows.
            after: Number of rows in ``gibberish`` for `id` after adding the rows.

        """
        query = f"SELECT * FROM gibberish WHERE id = {identifier}"
        results = self.dbc.execute(query)
        assert len(results.fetchall()) == before
        # Session requires mapped classes to interact with the database
        Base = automap_base()
        Base.prepare(self.dbc.connect(), reflect=True)
        Gibberish = Base.classes.gibberish
        # Ignore IntegrityError raised when committing the new tags as some parametrizations will force it
        try:
            with self.dbc.session_scope() as session:
                rows = [Gibberish(id=identifier, **row1), Gibberish(id=identifier, **row2)]
                session.add_all(rows)
        except IntegrityError:
            pass
        results = self.dbc.execute(query)
        assert len(results.fetchall()) == after

    @pytest.mark.dependency(depends=["test_init", "test_connect", "test_exec1", "test_exec2"], scope="class")
    def test_test_session_scope(self) -> None:
        """Tests :meth:`DBConnection.test_session_scope()` method."""
        # Session requires mapped classes to interact with the database
        Base = automap_base()
        Base.prepare(self.dbc.connect(), reflect=True)
        Gibberish = Base.classes.gibberish
        # Check that the tags added during the context manager are removed afterwards
        identifier = 8
        with self.dbc.test_session_scope() as session:
            results = session.query(Gibberish).filter_by(id=identifier)
            assert not results.all(), f"ID {identifier} shoud not have any entries"
            rows = [
                Gibberish(id=identifier, grp="grp7", value=15),
                Gibberish(id=identifier, grp="grp8", value=25),
            ]
            session.add_all(rows)
            session.commit()
            results = session.query(Gibberish).filter_by(id=identifier)
            assert len(results.all()) == 2, f"ID {identifier} should have two rows"
        results = self.dbc.execute(f"SELECT * FROM gibberish WHERE id = {identifier}")
        if self.dbc.dialect == "sqlite" or (
            self.dbc.dialect == "mysql"
            and self.dbc.tables["gibberish"].dialect_options["mysql"]["engine"] == "MyISAM"
        ):
            assert (
                len(results.all()) == 2
            ), f"SQLite/MyISAM: 2 rows have been permanently added to ID {identifier}"
        else:
            assert not results.fetchall(), f"No entries should have been permanently added to ID {identifier}"
