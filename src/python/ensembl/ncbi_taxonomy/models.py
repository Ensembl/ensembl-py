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
"""NCBI Taxonomy database ORM."""
# Ignore some pylint and mypy checks due to the nature of SQLAlchemy ORMs
# pylint: disable=missing-class-docstring
# mypy: disable-error-code="misc, valid-type"

from sqlalchemy import (
    Column,
    ForeignKey,
    join,
)
from sqlalchemy.dialects.mysql import (
    INTEGER,
    TINYINT,
    VARCHAR,
    CHAR,
)
from sqlalchemy.orm import (
    relationship,
    column_property,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NCBITaxaNode(Base):
    __tablename__ = "ncbi_taxa_node"

    taxon_id = Column(INTEGER(10), primary_key=True)
    parent_id = Column(INTEGER(10), ForeignKey('ncbi_taxa_node.taxon_id'), nullable=False, index=True)
    rank = Column(CHAR(32), nullable=False, index=True)
    genbank_hidden_flag = Column(TINYINT(1), nullable=False, default=0)
    left_index = Column(INTEGER(10), nullable=False, default=0, index=True)
    right_index = Column(INTEGER(10), nullable=False, default=0, index=True)
    root_id = Column(INTEGER(10), nullable=False, default=1)

    parent = relationship("NCBITaxaNode", remote_side=[taxon_id])
    children = relationship("NCBITaxaName")


class NCBITaxaName(Base):
    __tablename__ = "ncbi_taxa_name"

    taxon_id = Column(INTEGER(10), ForeignKey("ncbi_taxa_node.taxon_id"), index=True, primary_key=True)
    name = Column(VARCHAR(500), index=True, primary_key=True)
    name_class = Column(VARCHAR(50), nullable=False, index=True)


class NCBITaxonomy(Base):

    ncbi_taxa_name_table = NCBITaxaName.__table__
    ncbi_taxa_node_table = NCBITaxaNode.__table__

    name_node_join = join(ncbi_taxa_name_table, ncbi_taxa_node_table)

    __table__ = name_node_join

    taxon_id = column_property(ncbi_taxa_name_table.c.taxon_id, ncbi_taxa_node_table.c.taxon_id)
