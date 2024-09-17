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
"""Check the current ensembl-py core model against a core created from Ensembl SQL.
This script gets one row for each table in the ORM to check that SQLAlchemy can correctly query the table.
If not, it will show the `OperationalError` exception to explain what is wrong in the ORM.

Use this script to check the ORM (and fix it if needed).
"""

import logging

from ensembl.core.models import Base
from ensembl.utils.database import DBConnection
from ensembl.utils.argparse import ArgumentParser
from ensembl.utils.logging import init_logging_with_args
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, OperationalError, ProgrammingError
from sqlalchemy.orm import Session


def check_tables(session: Session, only_table: str = "") -> None:
    """Load data from a core using the ORM to check for any discrepancies in the definitions.

    Args:
        session: SQLAlchemy session.
        only_table: Only check this one table instead of all of the tables defined in the ORM.
    """
    success = []
    errors = []
    for table_name, table in Base.metadata.tables.items():
        if isinstance(table_name, tuple):
            table_name = table_name[0]
        if only_table and table_name != only_table:
            continue
        logging.debug(f"Check table {table_name}")
        stmt = select(table)
        try:
            session.execute(stmt).one()
            success.append(table_name)
        except (NoResultFound, MultipleResultsFound):
            success.append(table_name)
        except (OperationalError, ProgrammingError) as err:
            # Show the problematic query and continue
            logging.warning(f"{table_name}: {err}")
            errors.append(table_name)

    logging.info(f"{len(success)} tables successfully queried with the ORM")
    if errors:
        logging.warning(f"{len(errors)} tables failed to be queried with the ORM: {', '.join(errors)}")
    else:
        logging.info("No errors found")


def main() -> None:
    """Main script entry-point."""
    parser = ArgumentParser(description=__doc__)
    parser.add_server_arguments(include_database=True, help="Ensembl MySQL core database")
    parser.add_argument("--table", type=str, help="Test this one table only")
    parser.add_log_arguments(add_log_file=True)
    args = parser.parse_args()
    init_logging_with_args(args)
    dbc = DBConnection(args.url, reflect=False)
    with dbc.session_scope() as session:
        check_tables(session, only_table=args.table)


if __name__ == "__main__":
    main()
