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

from sqlalchemy import (Column, Index, ForeignKey, text)
from sqlalchemy.dialects.mysql import (INTEGER, VARCHAR, BOOLEAN)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChecksumXref(Base):
  __tablename__ = "checksum_xref"
  __table_args__ = (
    Index("checksum_idx", "checksum", mysql_length=10),
  )

  checksum_xref_id = Column(INTEGER, primary_key=True, autoincrement=True)
  source_id        = Column(INTEGER, nullable=False)
  accession        = Column(VARCHAR(14), nullable=False)
  checksum         = Column(VARCHAR(32), nullable=False)

class Source(Base):
  __tablename__ = "source"

  source_id = Column(INTEGER(10), primary_key=True, autoincrement=True)
  name      = Column(VARCHAR(128), index=True, unique=True)
  active    = Column(BOOLEAN, nullable=False, server_default=text("1"))
  parser    = Column(VARCHAR(128))

class Version(Base):
  __tablename__ = "version"
  __table_args__ = (
    Index("version_idx", "source_id", "revision")
  )

  version_id = Column(INTEGER(10), primary_key=True, autoincrement=True)
  source_id  = Column(INTEGER(10), ForeignKey("source.source_id"))
  revision   = Column(VARCHAR(255))
  count_seen = Column(INTEGER(10), nullable=False)
  uri        = Column(VARCHAR(255))
  index_uri  = Column(VARCHAR(255))
  clean_uri  = Column(VARCHAR(255))
  preparse   = Column(BOOLEAN, nullable=False, server_default=text("0"))
