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
"""Xref Source database ORM."""
# Ignore some pylint and mypy checks due to the nature of SQLAlchemy ORMs
# pylint: disable=missing-class-docstring,too-many-lines
# mypy: disable-error-code="misc, valid-type"

from sqlalchemy import Column, Index, ForeignKey, text
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ChecksumXref(Base):
    __tablename__ = "checksum_xref"
    __table_args__ = (Index("checksum_idx", "checksum", mysql_length=10),)

    checksum_xref_id: Column = Column(INTEGER, primary_key=True, autoincrement=True)
    source_id: Column = Column(INTEGER, nullable=False)
    accession: Column = Column(VARCHAR(14), nullable=False)
    checksum: Column = Column(VARCHAR(32), nullable=False)


class Source(Base):
    __tablename__ = "source"

    source_id: Column = Column(INTEGER(10), primary_key=True, autoincrement=True)
    name: Column = Column(VARCHAR(128), index=True, unique=True)
    active: Column = Column(BOOLEAN, nullable=False, server_default=text("1"))
    parser: Column = Column(VARCHAR(128))


class Version(Base):
    __tablename__ = "version"
    __table_args__ = (Index("version_idx", "source_id", "revision"),)

    version_id: Column = Column(INTEGER(10), primary_key=True, autoincrement=True)
    source_id: Column = Column(INTEGER(10), ForeignKey("source.source_id"))
    revision: Column = Column(VARCHAR(255))
    count_seen: Column = Column(INTEGER(10), nullable=False)
    uri: Column = Column(VARCHAR(255))
    index_uri: Column = Column(VARCHAR(255))
    clean_uri: Column = Column(VARCHAR(255))
    preparse: Column = Column(BOOLEAN, nullable=False, server_default=text("0"))
