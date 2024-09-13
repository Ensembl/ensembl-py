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
This script gets one row for each table in the ORM to check that SQLalchemy can correctly query the table.
If not, it will show the OperationalError exception to explain what is wrong in the ORM.

Use this script this check the ORM and fix it.
"""

import logging

from ensembl.utils.database import DBConnection
from ensembl.utils.argparse import ArgumentParser
from ensembl.utils.logging import init_logging_with_args
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, OperationalError
from sqlalchemy.orm import Session

from ensembl.core.models import Base

def check_tables(session: Session) -> None:
    success = []
    errors = []
    for table_name, table in Base.metadata.tables.items():
        logging.debug(f"Check table {table_name}")
        stmt = select(table)
        try:
            session.execute(stmt).one()
            success.append(table_name)
        except (NoResultFound, MultipleResultsFound):
            success.append(table_name)
            pass
        except OperationalError as err:
            # Show the problematic query and continue
            logging.warning(f"{table_name}: {err}")
            errors.append(table_name)
    
    logging.info(f"{len(success)} tables successfully queried with the ORM")
    if errors:
        logging.warning(f"{len(errors)} tables failed to be queried with the ORM: {", ".join(errors)}")
    else:
        logging.info("No errors found")

def main() -> None:
    """Main script entry-point."""
    parser = ArgumentParser(
        description=__doc__
    )
    parser.add_argument("--url", required=True, type=str, help="MySQL URL to a core database to get tables data from")
    parser.add_log_arguments(add_log_file=True)
    args = parser.parse_args()
    init_logging_with_args(args)

    dbc = DBConnection(args.url, reflect=False)
    with dbc.session_scope() as session:
        check_tables(session)

if __name__ == "__main__":
    main()
