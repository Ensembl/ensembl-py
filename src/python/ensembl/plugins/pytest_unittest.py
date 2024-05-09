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
"""Pytest plugin with Ensembl's Python unit testing plugins, hooks and fixtures."""
# Disable all the redefined-outer-name violations due to how pytest fixtures work
# pylint: disable=redefined-outer-name

from contextlib import nullcontext
from difflib import unified_diff
import os
from pathlib import Path
import re
from typing import Any, Callable, Dict, Generator, Optional

import pytest
from pytest import Config, FixtureRequest, Parser
from _pytest.python_api import RaisesContext
import sqlalchemy

from ensembl.database import UnitTestDB


def pytest_addoption(parser: Parser) -> None:
    """Registers argparse-style options for Ensembl's unit testing.

    `Pytest initialisation hook
    <https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_addoption>`_.

    Args:
        parser: Parser for command line arguments and ini-file values.

    """
    # Add the Ensembl unitary test parameters to pytest parser
    group = parser.getgroup("ensembl unit testing")
    group.addoption(
        "--server",
        action="store",
        metavar="URL",
        dest="server",
        required=False,
        default=os.getenv("DB_HOST", "sqlite:///"),
        help="URL to the server where to create the test database(s).",
    )
    group.addoption(
        "--keep-data",
        action="store_true",
        dest="keep_data",
        required=False,
        help="Do not remove test databases. Default: False",
    )


def pytest_report_header(config: Config) -> str:
    """Presents extra information in the report header.

    Args:
        config: Access to configuration values, pluginmanager and plugin hooks.

    """
    server = config.getoption("server")
    server = re.sub(r"(//[^/]+:).*(@)", r"\1xxxxxx\2", server)
    return f"server: {server}"


def pytest_configure(config: Config) -> None:
    """Adds global variables and configuration attributes required by Ensembl's unit tests.

    `Pytest initialisation hook
    <https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_configure>`_.

    Args:
        config: Access to configuration values, pluginmanager and plugin hooks.

    """
    # Load server information
    server_url = sqlalchemy.engine.url.make_url(config.getoption("server"))
    # If password starts with "$", treat it as an environment variable that needs to be resolved
    if server_url.password and server_url.password.startswith("$"):
        server_url = server_url.set(password=os.environ[server_url.password[1:]])
        config.option.server = str(server_url)


def pytest_make_parametrize_id(val: Any) -> str:
    """Returns a readable string representation of `val` that will be used by @pytest.mark.parametrize calls.

    `Pytest collection hook
    <https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_make_parametrize_id>`_.

    Args:
        val: The parametrized value.

    """
    if isinstance(val, nullcontext):
        return "No error"
    if isinstance(val, RaisesContext):
        return str(val.expected_exception)
    return str(val)


@pytest.fixture(name="assert_files")
def fixture_assert_files() -> Callable[[Path, Path], None]:
    """Returns a function that asserts if two files are equal and shows a diff if they differ."""

    def _assert_files(result_path: Path, expected_path: Path) -> None:
        with open(result_path, "r") as result_fh:
            results = result_fh.readlines()
        with open(expected_path, "r") as expected_fh:
            expected = expected_fh.readlines()
        files_diff = list(
            unified_diff(
                results,
                expected,
                fromfile=f"Test-made file {result_path.name}",
                tofile=f"Expected file {expected_path.name}",
            )
        )
        assert_message = f"Test-made and expected files differ\n{' '.join(files_diff)}"
        assert len(files_diff) == 0, assert_message

    return _assert_files


@pytest.fixture(name="data_dir", scope="module")
def local_data_dir(request: FixtureRequest) -> Path:
    """Returns the path to the test data folder matching the test's name.

    Args:
        request: Fixture providing information of the requesting test function.

    """
    return Path(request.module.__file__).with_suffix("")


@pytest.fixture(scope="session")
def shared_data_dir(pytestconfig: Config) -> Path:
    """Returns the path to the shared test data folder.

    Args:
        pytestconfig: Session-scoped fixture that returns the session's `pytest.Config` object.

    Raises:
        IOError: If `[src/[python/]]tests/data` folder does not exists from the root of the repository.

    """
    shared_data_path = pytestconfig.rootpath / "src/python/tests/data"
    if shared_data_path.is_dir():
        return shared_data_path
    shared_data_path = pytestconfig.rootpath / "src/tests/data"
    if shared_data_path.is_dir():
        return shared_data_path
    shared_data_path = pytestconfig.rootpath / "tests/data"
    if shared_data_path.is_dir():
        return shared_data_path
    raise IOError("No shared test data folder found")


@pytest.fixture(name="db_factory", scope="session")
def db_factory_(request: FixtureRequest, shared_data_dir: Path) -> Generator:
    """Yields a unit test database (:class:`UnitTestDB`) factory.

    Args:
        request: Access to the requesting test context.
        shared_data_dir: Path to the shared test data folder.

    """
    created: Dict[str, UnitTestDB] = {}
    server_url = request.config.getoption("server")

    def db_factory(src: os.PathLike, name: Optional[str] = None) -> UnitTestDB:
        """Returns a unit test database (:class:`UnitTestDB`) object.

        Args:
            src: Directory path where the test database schema and content files are located. If a relative
                path is provided, the root folder will be ``src/python/tests/databases``.
            name: Name to give to the new database. See :meth:`UnitTestDB.__init__()` for more information.

        """
        src_path = Path(src) if os.path.isabs(src) else shared_data_dir / src
        db_key = name if name else src_path.name
        return created.setdefault(db_key, UnitTestDB(server_url, src_path, name))

    yield db_factory
    # Drop all unit test databases unless the user has requested to keep them
    if not request.config.getoption("keep_data"):
        for test_db in created.values():
            test_db.drop()


@pytest.fixture(scope="session")
def db(request: FixtureRequest, db_factory: Callable) -> Generator:
    """Returns a unit test database (:class:`UnitTestDB`) object.

    Requires a dictionary with keys `src` (mandatory) and `name` (optional) passed via `request.param`. See
    :meth:`db_factory()` for details about each key's value. This fixture is a wrapper of :meth:`db_factory()`
    intended to be used via indirect parametrization, for example::

        @pytest.mark.parametrize("db", [{'src': 'master'}], indirect=True)
        def test_method(..., db: UnitTestDB, ...):

    Args:
        request: Access to the requesting test context.

    """
    return db_factory(request.param["src"], request.param.get("name", None))


@pytest.fixture(scope="session")
def multi_dbs(request: FixtureRequest, db_factory: Callable) -> Dict:
    """Returns a dictionary of unit test database (:class:`UnitTestDB`) objects with the database name as key.

    Requires a list of dictionaries, each with keys `src` (mandatory) and `name` (optional), passed via
    `request.param`. See :meth:`db_factory()` for details about each key's value. This fixture is a wrapper of
    :meth:`db_factory()` intended to be used via indirect parametrization, for example::

        @pytest.mark.parametrize("multi_dbs", [[{'src': 'master'}, {'src': 'master', 'name': 'master2'}]],
                                 indirect=True)
        def test_method(..., multi_dbs: Dict[str, UnitTestDB], ...):

    Args:
        request: Access to the requesting test context.

    """
    databases = {}
    for element in request.param:
        src = Path(element["src"])
        name = element.get("name", None)
        key = name if name else src.name
        databases[key] = db_factory(src, name)
    return databases
