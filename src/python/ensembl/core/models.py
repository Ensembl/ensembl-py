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
"""Ensembl Core database ORM."""
# Ignore some pylint and mypy checks due to the nature of SQLAlchemy ORMs
# pylint: disable=missing-class-docstring,too-many-lines,fixme
# mypy: disable-error-code="misc, valid-type"

# WIP: This module is not complete nor fully tested and will most likely change its public interface
# TODO:
#   - Please help defining/fixing relationships.
#     There are several relationships that have not been mapped yet, please help
#     adding them to the models if you find they're missing
#     https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
#   - Please help with better names.
#     Class names and attributes were generated directly
#     from the SQL schema but might not be suitable for a ORM.
#     For instance, several class attributes are prepended with the class name.
#     That's redundant most of the times and will result in less readable code.
#     Some class names are somehow reserved (e.g. class Meta) and some attributes names
#     are actually reserved (e.g. type, map, id) please help changing them into
#     meaningful ones

from typing import Any

import sqlalchemy
from sqlalchemy import (
    Column,
    DECIMAL,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.mysql import (
    BIGINT,
    DOUBLE,
    INTEGER,
    LONGTEXT,
    MEDIUMTEXT,
    SET,
    SMALLINT,
    TINYINT,
    TINYTEXT,
    VARCHAR,
)
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class AltAlleleGroup(Base):
    __tablename__ = "alt_allele_group"

    alt_allele_group_id: Column = Column(INTEGER(10), primary_key=True)


class Analysis(Base):
    __tablename__ = "analysis"

    analysis_id: Column = Column(SMALLINT(5), primary_key=True)
    created: Column = Column(DateTime)
    logic_name: Column = Column(String(128), nullable=False, unique=True)
    db: Column = Column(String(120))
    db_version: Column = Column(String(40))
    db_file: Column = Column(String(120))
    program: Column = Column(String(80))
    program_version: Column = Column(String(40))
    program_file: Column = Column(String(80))
    parameters: Column = Column(Text)
    module: Column = Column(String(80))
    module_version: Column = Column(String(40))
    gff_source: Column = Column(String(40))
    gff_feature: Column = Column(String(40))


class AssociatedGroup(Base):
    __tablename__ = "associated_group"

    associated_group_id: Column = Column(INTEGER(10), primary_key=True)
    description: Column = Column(String(128))


class AttribType(Base):
    __tablename__ = "attrib_type"

    attrib_type_id: Column = Column(SMALLINT(5), primary_key=True)
    code: Column = Column(String(20), nullable=False, unique=True, server_default=text("''"))
    name: Column = Column(String(255), nullable=False, server_default=text("''"))
    description: Column = Column(Text)

    seq_region_attrib = relationship("SeqRegionAttrib", back_populates="attrib_type")


class Biotype(Base):
    __tablename__ = "biotype"
    __table_args__ = (Index("name_type_idx", "name", "object_type", unique=True),)

    biotype_id: Column = Column(INTEGER(10), primary_key=True)
    name: Column = Column(String(64), nullable=False)
    object_type: Column = Column(Enum("gene", "transcript"), nullable=False, server_default=text("'gene'"))
    db_type: Column = Column(
        SET(
            "cdna",
            "core",
            "coreexpressionatlas",
            "coreexpressionest",
            "coreexpressiongnf",
            "funcgen",
            "otherfeatures",
            "rnaseq",
            "variation",
            "vega",
            "presite",
            "sangervega",
        ),
        nullable=False,
        server_default=text("'core'"),
    )
    attrib_type_id: Column = Column(INTEGER(11))
    description: Column = Column(Text)
    biotype_group: Column = Column(
        Enum(
            "coding",
            "pseudogene",
            "snoncoding",
            "lnoncoding",
            "mnoncoding",
            "LRG",
            "undefined",
            "no_group",
        )
    )
    so_acc: Column = Column(String(64))
    so_term: Column = Column(String(1023))


class CoordSystem(Base):
    __tablename__ = "coord_system"
    __table_args__ = (
        Index("name_idx", "name", "version", "species_id", unique=True),
        Index("rank_idx", "rank", "species_id", unique=True),
    )

    coord_system_id: Column = Column(INTEGER(10), primary_key=True)
    species_id: Column = Column(INTEGER(10), nullable=False, index=True, server_default=text("'1'"))
    name: Column = Column(String(40), nullable=False)
    version: Column = Column(String(255))
    rank: Column = Column(INTEGER(11), nullable=False)
    attrib: Column = Column(SET("default_version", "sequence_level"))
    # Many to one relationship
    seq_region = relationship("SeqRegion", back_populates="coord_system")
    meta = relationship("Meta", back_populates="coord_system")


class Ditag(Base):
    __tablename__ = "ditag"

    ditag_id: Column = Column(INTEGER(10), primary_key=True)
    name: Column = Column(String(30), nullable=False)
    tag_type: Column = Column("type", String(30), nullable=False)
    tag_count: Column = Column(SMALLINT(6), nullable=False, server_default=text("'1'"))
    sequence: Column = Column(TINYTEXT, nullable=False)


class DNAAlignFeatureAttrib(Base):
    __tablename__ = "dna_align_feature_attrib"
    __table_args__ = (
        Index(
            "dna_align_feature_attribx",
            "dna_align_feature_id",
            "attrib_type_id",
            "value",
            unique=True,
            mysql_length={"value": 10},
        ),
        Index("ditag_type_val_idx", "attrib_type_id", "value", mysql_length={"value": 10}),
        Index("ditag_value_idx", "value", mysql_length=10),
    )

    dna_align_feature_attrib_id: Column = Column(INTEGER(10), primary_key=True)
    dna_align_feature_id: Column = Column(
        INTEGER(10), ForeignKey("dna_align_feature.dna_align_feature_id"), nullable=False, index=True
    )
    attrib_type_id: Column = Column(SMALLINT(5), nullable=False)
    value: Column = Column(Text, nullable=False)


class ExternalDb(Base):
    __tablename__ = "external_db"
    __table_args__ = (Index("db_name_db_release_idx", "db_name", "db_release", unique=True),)

    external_db_id: Column = Column(INTEGER(10), primary_key=True)
    db_name: Column = Column(String(100), nullable=False)
    db_release: Column = Column(String(255))
    status: Column = Column(Enum("KNOWNXREF", "KNOWN", "XREF", "PRED", "ORTH", "PSEUDO"), nullable=False)
    priority: Column = Column(INTEGER(11), nullable=False)
    db_display_name: Column = Column(String(255))
    db_type: Column = Column(
        "type",
        Enum(
            "ARRAY",
            "ALT_TRANS",
            "ALT_GENE",
            "MISC",
            "LIT",
            "PRIMARY_DB_SYNONYM",
            "ENSEMBL",
        ),
        nullable=False,
    )
    secondary_db_name: Column = Column(String(255))
    secondary_db_table: Column = Column(String(255))
    description: Column = Column(Text)
    seq_region_synonym = relationship("SeqRegionSynonym", back_populates="external_db")


class Gene(Base):
    __tablename__ = "gene"
    __table_args__ = (
        Index("gene_seq_region_idx", "seq_region_id", "seq_region_start"),
        Index("gene_stable_id_idx", "stable_id", "version"),
    )

    gene_id: Column = Column(INTEGER(10), primary_key=True)
    biotype: Column = Column(String(40), nullable=False)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(2), nullable=False)
    display_xref_id: Column = Column(ForeignKey("xref.xref_id"), index=True)
    source: Column = Column(String(40), nullable=False)
    description: Column = Column(Text)
    is_current: Column = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    canonical_transcript_id: Column = Column(
        ForeignKey("transcript.transcript_id"),
        nullable=False,
        index=True,
    )
    stable_id: Column = Column(String(128))
    version: Column = Column(SMALLINT(5))
    created_date: Column = Column(DateTime)
    modified_date: Column = Column(DateTime)

    analysis = relationship("Analysis", primaryjoin="Gene.analysis_id == Analysis.analysis_id")
    canonical_transcript = relationship(
        "Transcript",
        primaryjoin="Gene.canonical_transcript_id == Transcript.transcript_id",
    )
    display_xref = relationship("Xref", primaryjoin="Gene.display_xref_id == Xref.xref_id")
    seq_region = relationship("SeqRegion", primaryjoin="Gene.seq_region_id == SeqRegion.seq_region_id")


class GenomeStatistics(Base):
    __tablename__ = "genome_statistics"
    __table_args__ = (Index("stats_uniq", "statistic", "attrib_type_id", "species_id", unique=True),)

    genome_statistics_id: Column = Column(INTEGER(10), primary_key=True)
    statistic: Column = Column(String(128), nullable=False)
    value: Column = Column(BIGINT(11), nullable=False, server_default=text("'0'"))
    species_id: Column = Column(INTEGER(10), server_default=text("'1'"))
    attrib_type_id: Column = Column(INTEGER(10))
    timestamp: Column = Column(DateTime)


t_interpro = Table(
    "interpro",
    metadata,
    Column("interpro_ac", String(40), nullable=False),
    Column("id", VARCHAR(40), nullable=False, index=True),
    Index("accession_idx", "interpro_ac", "id", unique=True),
)


class Map(Base):
    __tablename__ = "map"

    map_id: Column = Column(INTEGER(10), primary_key=True)
    map_name: Column = Column(String(30), nullable=False)


class MappingSession(Base):
    __tablename__ = "mapping_session"

    mapping_session_id: Column = Column(INTEGER(10), primary_key=True)
    old_db_name: Column = Column(String(80), nullable=False, server_default=text("''"))
    new_db_name: Column = Column(String(80), nullable=False, server_default=text("''"))
    old_release: Column = Column(String(5), nullable=False, server_default=text("''"))
    new_release: Column = Column(String(5), nullable=False, server_default=text("''"))
    old_assembly: Column = Column(String(80), nullable=False, server_default=text("''"))
    new_assembly: Column = Column(String(80), nullable=False, server_default=text("''"))
    created: Column = Column(DateTime, nullable=False)


class MappingSet(Base):
    __tablename__ = "mapping_set"
    __table_args__ = (Index("mapping_idx", "internal_schema_build", "external_schema_build", unique=True),)

    mapping_set_id: Column = Column(INTEGER(10), primary_key=True)
    internal_schema_build: Column = Column(String(20), nullable=False)
    external_schema_build: Column = Column(String(20), nullable=False)


class Marker(Base):
    __tablename__ = "marker"
    __table_args__ = (Index("marker_idx", "marker_id", "priority"),)

    marker_id: Column = Column(INTEGER(10), primary_key=True)
    display_marker_synonym_id: Column = Column(
        ForeignKey("marker_synonym.marker_synonym_id"),
        index=True,
    )
    left_primer: Column = Column(String(100), nullable=False)
    right_primer: Column = Column(String(100), nullable=False)
    min_primer_dist: Column = Column(INTEGER(10), nullable=False)
    max_primer_dist: Column = Column(INTEGER(10), nullable=False)
    priority: Column = Column(INTEGER(11))
    marker_type: Column = Column("type", Enum("est", "microsatellite"))

    display_marker_synonym = relationship(
        "MarkerSynonym",
        primaryjoin="Marker.display_marker_synonym_id == MarkerSynonym.marker_synonym_id",
    )


class MarkerSynonym(Base):
    __tablename__ = "marker_synonym"
    __table_args__ = (Index("marker_synonym_idx", "marker_synonym_id", "name"),)

    marker_synonym_id: Column = Column(INTEGER(10), primary_key=True)
    marker_id: Column = Column(
        ForeignKey("marker.marker_id"),
        nullable=False,
        index=True,
    )
    source: Column = Column(String(20))
    name: Column = Column(String(50))

    marker = relationship("Marker", primaryjoin="MarkerSynonym.marker_id == Marker.marker_id")


class PeptideArchive(Base):
    __tablename__ = "peptide_archive"

    peptide_archive_id: Column = Column(INTEGER(10), primary_key=True)
    md5_checksum: Column = Column(String(32), index=True)
    peptide_seq: Column = Column(MEDIUMTEXT, nullable=False)


class RepeatConsensus(Base):
    __tablename__ = "repeat_consensus"
    __table_args__ = (Index("repeat_consensus_idx", "repeat_consensus", unique=True, mysql_length=10),)

    repeat_consensus_id: Column = Column(INTEGER(10), primary_key=True)
    repeat_name: Column = Column(String(255), nullable=False, index=True)
    repeat_class: Column = Column(String(100), nullable=False, index=True)
    repeat_type: Column = Column(String(40), nullable=False, index=True)
    repeat_consensus: Column = Column(Text)


class Rnaproduct(Base):
    __tablename__ = "rnaproduct"
    __table_args__ = (Index("rnaproduct_stable_id_idx", "stable_id", "version"),)

    rnaproduct_id: Column = Column(INTEGER(10), primary_key=True)
    rnaproduct_type_id: Column = Column(SMALLINT(5), nullable=False)
    transcript_id: Column = Column(INTEGER(10), nullable=False, index=True)
    seq_start: Column = Column(INTEGER(10), nullable=False)
    start_exon_id: Column = Column(INTEGER(10))
    seq_end: Column = Column(INTEGER(10), nullable=False)
    end_exon_id: Column = Column(INTEGER(10))
    stable_id: Column = Column(String(128))
    version: Column = Column(SMALLINT(5))
    created_date: Column = Column(DateTime)
    modified_date: Column = Column(DateTime)


class RNAproductAttrib(Base):
    __tablename__ = "rnaproduct_attrib"
    __table_args__ = (
        Index(
            "rnaproduct_attribx",
            "rnaproduct_id",
            "attrib_type_id",
            "value",
            unique=True,
            mysql_length={"value": 10},
        ),
        Index("rnaproduct_type_val_idx", "attrib_type_id", "value", mysql_length={"value": 10}),
        Index("rnaproduct_value_idx", "value", mysql_length=10),
    )
    rnaproduct_attrib_id: Column = Column(INTEGER(10), primary_key=True)
    rnaproduct_id: Column = Column(ForeignKey("rnaproduct.rnaproduct_id"), nullable=False, index=True)
    attrib_type_id: Column = Column(SMALLINT(5), nullable=False)
    value: Column = Column(Text, nullable=False)


class RnaproductType(Base):
    __tablename__ = "rnaproduct_type"

    rnaproduct_type_id: Column = Column(SMALLINT(5), primary_key=True)
    code: Column = Column(String(20), nullable=False, unique=True, server_default=text("''"))
    name: Column = Column(String(255), nullable=False, server_default=text("''"))
    description: Column = Column(Text)


class Transcript(Base):
    __tablename__ = "transcript"
    __table_args__ = (
        Index("transcript_seq_region_idx", "seq_region_id", "seq_region_start"),
        Index("transcript_stable_id_idx", "stable_id", "version"),
    )

    transcript_id: Column = Column(INTEGER(10), primary_key=True)
    gene_id: Column = Column(ForeignKey("gene.gene_id"), index=True)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(2), nullable=False)
    display_xref_id: Column = Column(ForeignKey("xref.xref_id"), index=True)
    source: Column = Column(String(40), nullable=False, server_default=text("'ensembl'"))
    biotype: Column = Column(String(40), nullable=False)
    description: Column = Column(Text)
    is_current: Column = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    canonical_translation_id: Column = Column(
        ForeignKey("translation.translation_id"),
        unique=True,
    )
    stable_id: Column = Column(String(128))
    version: Column = Column(SMALLINT(5))
    created_date: Column = Column(DateTime)
    modified_date: Column = Column(DateTime)

    analysis = relationship("Analysis", primaryjoin="Transcript.analysis_id == Analysis.analysis_id")
    canonical_translation = relationship(
        "Translation",
        primaryjoin="Transcript.canonical_translation_id == Translation.translation_id",
    )
    display_xref = relationship("Xref", primaryjoin="Transcript.display_xref_id == Xref.xref_id")
    gene = relationship("Gene", primaryjoin="Transcript.gene_id == Gene.gene_id")
    seq_region = relationship("SeqRegion", primaryjoin="Transcript.seq_region_id == SeqRegion.seq_region_id")


class TranscriptIntronSupportingEvidence(Base):
    __tablename__ = "transcript_intron_supporting_evidence"

    transcript_id: Column = Column(INTEGER(10), primary_key=True, nullable=False, index=True)
    intron_supporting_evidence_id: Column = Column(INTEGER(10), primary_key=True, nullable=False)
    previous_exon_id: Column = Column(INTEGER(10), nullable=False)
    next_exon_id: Column = Column(INTEGER(10), nullable=False)


class Translation(Base):
    __tablename__ = "translation"
    __table_args__ = (Index("translation_stable_id_idx", "stable_id", "version"),)

    translation_id: Column = Column(INTEGER(10), primary_key=True)
    transcript_id: Column = Column(
        ForeignKey("transcript.transcript_id"),
        nullable=False,
        index=True,
    )
    seq_start: Column = Column(INTEGER(10), nullable=False)
    start_exon_id: Column = Column(
        ForeignKey("exon.exon_id"),
        nullable=False,
        index=True,
    )
    seq_end: Column = Column(INTEGER(10), nullable=False)
    end_exon_id: Column = Column(
        ForeignKey("exon.exon_id"),
        nullable=False,
        index=True,
    )
    stable_id: Column = Column(String(128))
    version: Column = Column(SMALLINT(5))
    created_date: Column = Column(DateTime)
    modified_date: Column = Column(DateTime)

    end_exon = relationship("Exon", primaryjoin="Translation.end_exon_id == Exon.exon_id")
    start_exon = relationship("Exon", primaryjoin="Translation.start_exon_id == Exon.exon_id")
    transcript = relationship(
        "Transcript",
        primaryjoin="Translation.transcript_id == Transcript.transcript_id",
    )


class UnmappedReason(Base):
    __tablename__ = "unmapped_reason"

    unmapped_reason_id: Column = Column(INTEGER(10), primary_key=True)
    summary_description: Column = Column(String(255))
    full_description: Column = Column(String(255))


class AltAllele(Base):
    __tablename__ = "alt_allele"
    __table_args__ = (Index("alt_allele_gene_id_idx", "gene_id", "alt_allele_group_id"),)

    alt_allele_id: Column = Column(INTEGER(10), primary_key=True)
    alt_allele_group_id: Column = Column(
        ForeignKey("alt_allele_group.alt_allele_group_id"),
        nullable=False,
        index=True,
    )
    gene_id: Column = Column(
        ForeignKey("gene.gene_id"),
        nullable=False,
        unique=True,
    )

    alt_allele_group = relationship(
        "AltAlleleGroup",
        primaryjoin="AltAllele.alt_allele_group_id == AltAlleleGroup.alt_allele_group_id",
    )
    gene = relationship("Gene", primaryjoin="AltAllele.gene_id == Gene.gene_id")


class AnalysisDescription(Base):
    __tablename__ = "analysis_description"

    analysis_id: Column = Column(
        SMALLINT(5),
        ForeignKey("analysis.analysis_id"),
        primary_key=True,
        nullable=False,
        unique=True,
    )
    description: Column = Column(Text)
    display_label: Column = Column(String(255), nullable=False)
    displayable: Column = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    web_data: Column = Column(Text)


class DataFile(Base):
    __tablename__ = "data_file"
    __table_args__ = (
        Index(
            "df_unq_idx",
            "coord_system_id",
            "analysis_id",
            "name",
            "file_type",
            unique=True,
        ),
    )

    data_file_id: Column = Column(INTEGER(10), primary_key=True)
    coord_system_id: Column = Column(
        ForeignKey("coord_system.coord_system_id"),
        nullable=False,
    )
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    name: Column = Column(String(100), nullable=False, index=True)
    version_lock: Column = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    absolute: Column = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    url: Column = Column(Text)
    file_type: Column = Column(Enum("BAM", "BAMCOV", "BIGBED", "BIGWIG", "VCF"))

    analysis = relationship("Analysis", primaryjoin="DataFile.analysis_id == Analysis.analysis_id")
    coord_system = relationship(
        "CoordSystem",
        primaryjoin="DataFile.coord_system_id == CoordSystem.coord_system_id",
    )


class DensityType(Base):
    __tablename__ = "density_type"
    __table_args__ = (Index("analysis_idx", "analysis_id", "block_size", "region_features", unique=True),)

    density_type_id: Column = Column(INTEGER(10), primary_key=True)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
    )
    block_size: Column = Column(INTEGER(11), nullable=False)
    region_features: Column = Column(INTEGER(11), nullable=False)
    value_type: Column = Column(Enum("sum", "ratio"), nullable=False)

    analysis = relationship("Analysis", primaryjoin="DensityType.analysis_id == Analysis.analysis_id")


t_gene_archive = Table(
    "gene_archive",
    metadata,
    Column("gene_stable_id", String(128), nullable=False),
    Column("gene_version", SMALLINT(6), nullable=False, server_default=text("'1'")),
    Column("transcript_stable_id", String(128), nullable=False),
    Column("transcript_version", SMALLINT(6), nullable=False, server_default=text("'1'")),
    Column("translation_stable_id", String(128)),
    Column("translation_version", SMALLINT(6), nullable=False, server_default=text("'1'")),
    Column(
        "peptide_archive_id",
        ForeignKey("peptide_archive.peptide_archive_id"),
        index=True,
    ),
    Column(
        "mapping_session_id",
        ForeignKey("mapping_session.mapping_session_id"),
        nullable=False,
        index=True,
    ),
    Index("transcript_idx", "transcript_stable_id", "transcript_version"),
    Index("translation_idx", "translation_stable_id", "translation_version"),
    Index("gene_idx", "gene_stable_id", "gene_version"),
)


class GeneAttrib(Base):
    __tablename__ = "gene_attrib"
    __table_args__ = (
        Index("gene_attribx", "gene_id", "attrib_type_id", "value", unique=True, mysql_length={"value": 10}),
        Index("gene_attrib_type_val_idx", "attrib_type_id", "value", mysql_length={"value": 10}),
        Index("gene_attrib_value_idx", "value", mysql_length=10),
    )

    gene_attrib_id: Column = Column(INTEGER(10), primary_key=True)
    gene_id: Column = Column(
        INTEGER(10),
        ForeignKey("gene.gene_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    attrib_type_id: Column = Column(
        SMALLINT(5),
        ForeignKey("attrib_type.attrib_type_id"),
        nullable=False,
        server_default=text("'0'"),
    )
    value: Column = Column(Text, nullable=False)


class MarkerMapLocation(Base):
    __tablename__ = "marker_map_location"
    __table_args__ = (Index("map_idx", "map_id", "chromosome_name", "position"),)

    marker_id: Column = Column(
        ForeignKey("marker.marker_id"),
        primary_key=True,
        nullable=False,
    )
    map_id: Column = Column(
        ForeignKey("map.map_id"),
        primary_key=True,
        nullable=False,
    )
    chromosome_name: Column = Column(String(15), nullable=False)
    marker_synonym_id: Column = Column(
        ForeignKey("marker_synonym.marker_synonym_id"),
        nullable=False,
        index=True,
    )
    position: Column = Column(String(15), nullable=False)
    lod_score: Column = Column(Float(asdecimal=True))

    map_r = relationship("Map", primaryjoin="MarkerMapLocation.map_id == Map.map_id")
    marker = relationship("Marker", primaryjoin="MarkerMapLocation.marker_id == Marker.marker_id")
    marker_synonym = relationship(
        "MarkerSynonym",
        primaryjoin="MarkerMapLocation.marker_synonym_id == MarkerSynonym.marker_synonym_id",
    )


class Meta(Base):
    __tablename__ = "meta"
    __table_args__ = (
        Index("species_value_idx", "species_id", "meta_value"),
        Index("species_key_value_idx", "species_id", "meta_key", "meta_value", unique=True),
    )

    meta_id: Column = Column(INTEGER(11), primary_key=True)
    species_id: Column = Column(
        ForeignKey("coord_system.species_id"),
        server_default=text("'1'"),
    )
    meta_key: Column = Column(String(40), nullable=False)
    meta_value: Column = Column(String(255), nullable=False)

    coord_system = relationship("CoordSystem", back_populates="meta")


class MetaCoord(Base):
    __tablename__ = "meta_coord"
    __table_args__ = (Index("cs_table_name_idx", "coord_system_id", "table_name", unique=True),)

    table_name: Column = Column(String(40), primary_key=True, nullable=False)
    coord_system_id: Column = Column(
        INTEGER(10),
        ForeignKey("coord_system.coord_system_id"),
        primary_key=True,
        nullable=False,
    )
    max_length: Column = Column(INTEGER(11))


class ProteinFeature(Base):
    __tablename__ = "protein_feature"
    __table_args__ = (
        Index(
            "aln_idx",
            "translation_id",
            "hit_name",
            "seq_start",
            "seq_end",
            "hit_start",
            "hit_end",
            "analysis_id",
            unique=True,
        ),
    )

    protein_feature_id: Column = Column(INTEGER(10), primary_key=True)
    translation_id: Column = Column(
        ForeignKey("translation.translation_id"),
        nullable=False,
        index=True,
    )
    seq_start: Column = Column(INTEGER(10), nullable=False)
    seq_end: Column = Column(INTEGER(10), nullable=False)
    hit_start: Column = Column(INTEGER(10), nullable=False)
    hit_end: Column = Column(INTEGER(10), nullable=False)
    hit_name: Column = Column(VARCHAR(40), nullable=False, index=True)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    score: Column = Column(Float(asdecimal=True))
    evalue: Column = Column(Float(asdecimal=True))
    perc_ident: Column = Column(Float)
    external_data: Column = Column(Text)
    hit_description: Column = Column(Text)
    cigar_line: Column = Column(Text)
    align_type: Column = Column(Enum("ensembl", "cigar", "cigarplus", "vulgar", "mdtag"))

    analysis = relationship("Analysis", primaryjoin="ProteinFeature.analysis_id == Analysis.analysis_id")
    translation = relationship(
        "Translation",
        primaryjoin="ProteinFeature.translation_id == Translation.translation_id",
    )


class SeqRegion(Base):
    __tablename__ = "seq_region"
    __table_args__ = (Index("name_cs_idx", "name", "coord_system_id", unique=True),)

    seq_region_id: Column = Column(INTEGER(10), primary_key=True)
    name: Column = Column(String(255), nullable=False)
    coord_system_id: Column = Column(
        ForeignKey("coord_system.coord_system_id"),
        nullable=False,
        index=True,
    )
    length: Column = Column(INTEGER(10), nullable=False)
    # Many to one relationship
    coord_system = relationship("CoordSystem", back_populates="seq_region")
    seq_region_attrib = relationship("SeqRegionAttrib", back_populates="seq_region")
    seq_region_synonym = relationship("SeqRegionSynonym", back_populates="seq_region")
    karyotype = relationship("Karyotype", back_populates="seq_region")


class Dna(SeqRegion):
    __tablename__ = "dna"

    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        primary_key=True,
    )
    sequence: Column = Column(LONGTEXT, nullable=False)

    seq_region = relationship(
        "SeqRegion",
        uselist=False,
        primaryjoin="Dna.seq_region_id == SeqRegion.seq_region_id",
    )


class StableIdEvent(Base):
    __tablename__ = "stable_id_event"
    __table_args__ = (
        Index(
            "uni_idx",
            "mapping_session_id",
            "old_stable_id",
            "new_stable_id",
            "type",
            unique=True,
        ),
    )

    old_stable_id: Column = Column(String(128), primary_key=True, index=True)
    old_version: Column = Column(SMALLINT(6))
    new_stable_id: Column = Column(String(128), primary_key=True, index=True)
    new_version: Column = Column(SMALLINT(6))
    mapping_session_id: Column = Column(
        INTEGER(10),
        ForeignKey("mapping_session.mapping_session_id"),
        primary_key=True,
        nullable=False,
        server_default=text("'0'"),
    )
    id_type: Column = Column(
        "type",
        Enum("gene", "transcript", "translation", "rnaproduct"),
        primary_key=True,
        nullable=False,
    )
    score: Column = Column(Float, nullable=False, server_default=text("'0'"))


class TranscriptAttrib(Base):
    __tablename__ = "transcript_attrib"
    __table_args__ = (
        Index("transcript_attrib_type_val_idx", "attrib_type_id", "value", mysql_length={"value": 10}),
        Index(
            "transcript_attribx",
            "transcript_id",
            "attrib_type_id",
            "value",
            unique=True,
            mysql_length={"value": 10},
        ),
        Index("transcript_attrib_value_idx", "value", mysql_length=10),
    )

    transcript_attrib_id: Column = Column(INTEGER(10), primary_key=True)
    transcript_id: Column = Column(
        INTEGER(10),
        ForeignKey("transcript.transcript_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    attrib_type_id: Column = Column(
        SMALLINT(5),
        ForeignKey("attrib_type.attrib_type_id"),
        nullable=False,
        server_default=text("'0'"),
    )
    value: Column = Column(Text, nullable=False)


class TranscriptSupportingFeature(Base):
    __tablename__ = "transcript_supporting_feature"
    __table_args__ = (
        Index("transcript_supporting_feature_idx", "feature_type", "feature_id"),
        Index(
            "transcript_supporting_feature_all_idx",
            "transcript_id",
            "feature_type",
            "feature_id",
            unique=True,
        ),
    )

    transcript_id: Column = Column(
        INTEGER(10),
        ForeignKey("transcript.transcript_id"),
        primary_key=True,
        nullable=False,
        server_default=text("'0'"),
    )
    feature_type: Column = Column(Enum("dna_align_feature", "protein_align_feature"), primary_key=True)
    feature_id: Column = Column(INTEGER(10), primary_key=True, nullable=False, server_default=text("'0'"))


class TranslationAttrib(Base):
    __tablename__ = ("translation_attrib",)
    __table_args__ = (
        Index("translation_attrib_type_val_idx", "attrib_type_id", "value", mysql_length={"value": 10}),
        Index(
            "translation_attribx",
            "translation_id",
            "attrib_type_id",
            "value",
            unique=True,
            mysql_length={"value": 10},
        ),
        Index("translation_attrib_value_idx", "value", mysql_length=10),
    )

    translation_attrib_id: Column = Column(INTEGER(10), primary_key=True)
    translation_id: Column = Column(
        ForeignKey("translation.translation_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    attrib_type_id: Column = Column(
        ForeignKey("attrib_type.attrib_type_id"),
        nullable=False,
        server_default=text("'0'"),
    )
    value: Column = Column(Text, nullable=False)


class UnmappedObject(Base):
    __tablename__ = "unmapped_object"
    __table_args__ = (
        Index(
            "unique_unmapped_obj_idx",
            "ensembl_id",
            "ensembl_object_type",
            "identifier",
            "unmapped_reason_id",
            "parent",
            "external_db_id",
            unique=True,
        ),
        Index("anal_exdb_idx", "analysis_id", "external_db_id"),
        Index("ext_db_identifier_idx", "external_db_id", "identifier"),
    )

    unmapped_object_id: Column = Column(INTEGER(10), primary_key=True)
    unmapped_object_type: Column = Column("type", Enum("xref", "cDNA", "Marker"), nullable=False)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
    )
    external_db_id: Column = Column(
        ForeignKey("external_db.external_db_id"),
    )
    identifier: Column = Column(String(255), nullable=False, index=True)
    unmapped_reason_id: Column = Column(
        ForeignKey("unmapped_reason.unmapped_reason_id"),
        nullable=False,
        index=True,
    )
    query_score: Column = Column(Float(asdecimal=True))
    target_score: Column = Column(Float(asdecimal=True))
    ensembl_id: Column = Column(INTEGER(10), server_default=text("'0'"))
    ensembl_object_type: Column = Column(
        Enum("RawContig", "Transcript", "Gene", "Translation"),
        server_default=text("'RawContig'"),
    )
    parent: Column = Column(String(255))

    analysis = relationship("Analysis", primaryjoin="UnmappedObject.analysis_id == Analysis.analysis_id")
    external_db = relationship(
        "ExternalDb",
        primaryjoin="UnmappedObject.external_db_id == ExternalDb.external_db_id",
    )
    unmapped_reason = relationship(
        "UnmappedReason",
        primaryjoin="UnmappedObject.unmapped_reason_id == UnmappedReason.unmapped_reason_id",
    )


class Xref(Base):
    __tablename__ = "xref"
    __table_args__ = (
        Index(
            "id_index",
            "dbprimary_acc",
            "external_db_id",
            "info_type",
            "info_text",
            "version",
            unique=True,
        ),
    )

    xref_id: Column = Column(INTEGER(10), primary_key=True)
    external_db_id: Column = Column(
        ForeignKey("external_db.external_db_id"),
        nullable=False,
        index=True,
    )
    dbprimary_acc: Column = Column(String(512), nullable=False)
    display_label: Column = Column(String(512), nullable=False, index=True)
    version: Column = Column(String(10))
    description: Column = Column(Text)
    info_type: Column = Column(
        Enum(
            "NONE",
            "PROJECTION",
            "MISC",
            "DEPENDENT",
            "DIRECT",
            "SEQUENCE_MATCH",
            "INFERRED_PAIR",
            "PROBE",
            "UNMAPPED",
            "COORDINATE_OVERLAP",
            "CHECKSUM",
        ),
        nullable=False,
        index=True,
        server_default=text("'NONE'"),
    )
    info_text: Column = Column(String(255), nullable=False, server_default=text("''"))

    external_db = relationship("ExternalDb", primaryjoin="Xref.external_db_id == ExternalDb.external_db_id")


t_alt_allele_attrib = Table(
    "alt_allele_attrib",
    metadata,
    Column(
        "alt_allele_id",
        ForeignKey("alt_allele.alt_allele_id"),
    ),
    Column(
        "attrib",
        Enum(
            "IS_REPRESENTATIVE",
            "IS_MOST_COMMON_ALLELE",
            "IN_CORRECTED_ASSEMBLY",
            "HAS_CODING_POTENTIAL",
            "IN_ARTIFICIALLY_DUPLICATED_ASSEMBLY",
            "IN_SYNTENIC_REGION",
            "HAS_SAME_UNDERLYING_DNA_SEQUENCE",
            "IN_BROKEN_ASSEMBLY_REGION",
            "IS_VALID_ALTERNATE",
            "SAME_AS_REPRESENTATIVE",
            "SAME_AS_ANOTHER_ALLELE",
            "MANUALLY_ASSIGNED",
            "AUTOMATICALLY_ASSIGNED",
        ),
    ),
    Index("aa_idx", "alt_allele_id", "attrib"),
)


class Assembly(Base):
    __tablename__ = "assembly"
    __table_args__ = (
        Index("asm_seq_region_idx", "asm_seq_region_id", "asm_start"),
        Index(
            "asm_all_idx",
            "asm_seq_region_id",
            "cmp_seq_region_id",
            "asm_start",
            "asm_end",
            "cmp_start",
            "cmp_end",
            "ori",
            unique=True,
        ),
    )

    asm_seq_region_id: Column = Column(
        INTEGER(10),
        ForeignKey("seq_region.seq_region_id"),
        primary_key=True,
        nullable=False,
    )
    cmp_seq_region_id: Column = Column(
        INTEGER(10),
        ForeignKey("seq_region.seq_region_id"),
        primary_key=True,
        nullable=False,
    )
    asm_start: Column = Column(INTEGER(10), primary_key=True, nullable=False)
    asm_end: Column = Column(INTEGER(10), primary_key=True, nullable=False)
    cmp_start: Column = Column(INTEGER(10), primary_key=True, nullable=False)
    cmp_end: Column = Column(INTEGER(10), primary_key=True, nullable=False)
    ori: Column = Column(TINYINT(4), primary_key=True, nullable=False)


class AssemblyException(Base):
    __tablename__ = "assembly_exception"
    __table_args__ = (
        Index("ex_idx", "exc_seq_region_id", "exc_seq_region_start"),
        Index("sr_idx", "seq_region_id", "seq_region_start"),
    )

    assembly_exception_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    exc_type: Column = Column(Enum("HAP", "PAR", "PATCH_FIX", "PATCH_NOVEL"), nullable=False)
    exc_seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    exc_seq_region_start: Column = Column(INTEGER(10), nullable=False)
    exc_seq_region_end: Column = Column(INTEGER(10), nullable=False)
    ori: Column = Column(INTEGER(11), nullable=False)

    exc_seq_region = relationship(
        "SeqRegion",
        primaryjoin="AssemblyException.exc_seq_region_id == SeqRegion.seq_region_id",
    )
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="AssemblyException.seq_region_id == SeqRegion.seq_region_id",
    )


class DensityFeature(Base):
    __tablename__ = "density_feature"
    __table_args__ = (
        Index("density_seq_region_idx", "density_type_id", "seq_region_id", "seq_region_start"),
    )

    density_feature_id: Column = Column(INTEGER(10), primary_key=True)
    density_type_id: Column = Column(
        ForeignKey("density_type.density_type_id"),
        nullable=False,
    )
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
        index=True,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    density_value: Column = Column(Float, nullable=False)

    density_type = relationship(
        "DensityType",
        primaryjoin="DensityFeature.density_type_id == DensityType.density_type_id",
    )
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="DensityFeature.seq_region_id == SeqRegion.seq_region_id",
    )


class DitagFeature(Base):
    __tablename__ = "ditag_feature"
    __table_args__ = (Index("ditag_seq_region_idx", "seq_region_id", "seq_region_start", "seq_region_end"),)

    ditag_feature_id: Column = Column(INTEGER(10), primary_key=True)
    ditag_id: Column = Column(
        ForeignKey("ditag.ditag_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    ditag_pair_id: Column = Column(INTEGER(10), nullable=False, index=True, server_default=text("'0'"))
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
        server_default=text("'0'"),
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False, server_default=text("'0'"))
    seq_region_end: Column = Column(INTEGER(10), nullable=False, server_default=text("'0'"))
    seq_region_strand: Column = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    hit_start: Column = Column(INTEGER(10), nullable=False, server_default=text("'0'"))
    hit_end: Column = Column(INTEGER(10), nullable=False, server_default=text("'0'"))
    hit_strand: Column = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    cigar_line: Column = Column(TINYTEXT, nullable=False)
    ditag_side: Column = Column(Enum("F", "L", "R"), nullable=False)

    analysis = relationship("Analysis", primaryjoin="DitagFeature.analysis_id == Analysis.analysis_id")
    ditag = relationship("Ditag", primaryjoin="DitagFeature.ditag_id == Ditag.ditag_id")
    seq_region = relationship(
        "SeqRegion", primaryjoin="DitagFeature.seq_region_id == SeqRegion.seq_region_id"
    )


class DnaAlignFeature(Base):
    __tablename__ = "dna_align_feature"
    __table_args__ = (
        Index("dna_align_seq_region_idx_2", "seq_region_id", "seq_region_start"),
        Index(
            "dna_align_seq_region_idx",
            "seq_region_id",
            "analysis_id",
            "seq_region_start",
            "score",
        ),
    )

    dna_align_feature_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(1), nullable=False)
    hit_start: Column = Column(INTEGER(11), nullable=False)
    hit_end: Column = Column(INTEGER(11), nullable=False)
    hit_strand: Column = Column(TINYINT(1), nullable=False)
    hit_name: Column = Column(String(40), nullable=False, index=True)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    score: Column = Column(Float(asdecimal=True))
    evalue: Column = Column(Float(asdecimal=True))
    perc_ident: Column = Column(Float)
    cigar_line: Column = Column(Text)
    external_db_id: Column = Column(
        ForeignKey("external_db.external_db_id"),
        index=True,
    )
    hcoverage: Column = Column(Float(asdecimal=True))
    align_type: Column = Column(Enum("ensembl", "cigar", "vulgar", "mdtag"), server_default=text("'ensembl'"))

    analysis = relationship("Analysis", primaryjoin="DnaAlignFeature.analysis_id == Analysis.analysis_id")
    external_db = relationship(
        "ExternalDb",
        primaryjoin="DnaAlignFeature.external_db_id == ExternalDb.external_db_id",
    )
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="DnaAlignFeature.seq_region_id == SeqRegion.seq_region_id",
    )


class Exon(Base):
    __tablename__ = "exon"
    __table_args__ = (
        Index("exon_seq_region_idx", "seq_region_id", "seq_region_start"),
        Index("exon_stable_id_idx", "stable_id", "version"),
    )

    exon_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(2), nullable=False)
    phase: Column = Column(TINYINT(2), nullable=False)
    end_phase: Column = Column(TINYINT(2), nullable=False)
    is_current: Column = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    is_constitutive: Column = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    stable_id: Column = Column(String(128))
    version: Column = Column(SMALLINT(5))
    created_date: Column = Column(DateTime)
    modified_date: Column = Column(DateTime)

    seq_region = relationship("SeqRegion", primaryjoin="Exon.seq_region_id == SeqRegion.seq_region_id")


class ExternalSynonym(Base):
    __tablename__ = "external_synonym"

    xref_id: Column = Column(
        ForeignKey("xref.xref_id"),
        primary_key=True,
        nullable=False,
    )
    synonym: Column = Column(String(100), primary_key=True, nullable=False, index=True)

    xref = relationship("Xref", primaryjoin="ExternalSynonym.xref_id == Xref.xref_id")


class IntronSupportingEvidence(Base):
    __tablename__ = "intron_supporting_evidence"
    __table_args__ = (
        Index(
            "analysis_id",
            "analysis_id",
            "seq_region_id",
            "seq_region_start",
            "seq_region_end",
            "seq_region_strand",
            "hit_name",
            unique=True,
        ),
        Index("intron_evidence_seq_region_idx", "seq_region_id", "seq_region_start"),
    )

    intron_supporting_evidence_id: Column = Column(INTEGER(10), primary_key=True)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
    )
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(2), nullable=False)
    hit_name: Column = Column(String(100), nullable=False)
    score: Column = Column(DECIMAL(10, 3))
    score_type: Column = Column(Enum("NONE", "DEPTH"), server_default=text("'NONE'"))
    is_splice_canonical: Column = Column(TINYINT(1), nullable=False, server_default=text("'0'"))

    analysis = relationship(
        "Analysis",
        primaryjoin="IntronSupportingEvidence.analysis_id == Analysis.analysis_id",
    )
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="IntronSupportingEvidence.seq_region_id == SeqRegion.seq_region_id",
    )


class Karyotype(Base):
    __tablename__ = "karyotype"
    __table_args__ = (Index("region_band_idx", "seq_region_id", "band"),)

    karyotype_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    band: Column = Column(String(40))
    stain: Column = Column(String(40))

    seq_region = relationship("SeqRegion", primaryjoin="Karyotype.seq_region_id == SeqRegion.seq_region_id")


class MarkerFeature(Base):
    __tablename__ = "marker_feature"
    __table_args__ = (Index("marker_seq_region_idx", "seq_region_id", "seq_region_start"),)

    marker_feature_id: Column = Column(INTEGER(10), primary_key=True)
    marker_id: Column = Column(
        ForeignKey("marker.marker_id"),
        nullable=False,
        index=True,
    )
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    map_weight: Column = Column(INTEGER(10))

    analysis = relationship("Analysis", primaryjoin="MarkerFeature.analysis_id == Analysis.analysis_id")
    marker = relationship("Marker", primaryjoin="MarkerFeature.marker_id == Marker.marker_id")
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="MarkerFeature.seq_region_id == SeqRegion.seq_region_id",
    )


t_misc_feature_misc_set = Table(
    "misc_feature_misc_set",
    metadata,
    Column(
        "misc_feature_id",
        ForeignKey("misc_feature.misc_feature_id"),
        primary_key=True,
        nullable=False,
        server_default=text("'0'"),
    ),
    Column(
        "misc_set_id",
        ForeignKey("misc_set.misc_set_id"),
        primary_key=True,
        nullable=False,
        server_default=text("'0'"),
    ),
    Index("reverse_idx", "misc_set_id", "misc_feature_id"),
)


class MiscSet(Base):
    __tablename__ = "misc_set"

    misc_set_id: Column = Column(SMALLINT(5), primary_key=True)
    code: Column = Column(String(25), nullable=False, unique=True, server_default=text("''"))
    name: Column = Column(String(255), nullable=False, server_default=text("''"))
    description: Column = Column(Text, nullable=False)
    max_length: Column = Column(INTEGER(10), nullable=False)

    # misc_features = relationship("MiscFeature", secondary=t_misc_feature_misc_set)


class MiscFeature(Base):
    __tablename__ = "misc_feature"
    __table_args__ = (Index("misc_seq_region_idx", "seq_region_id", "seq_region_start"),)

    misc_feature_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
        server_default=text("'0'"),
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False, server_default=text("'0'"))
    seq_region_end: Column = Column(INTEGER(10), nullable=False, server_default=text("'0'"))
    seq_region_strand: Column = Column(TINYINT(4), nullable=False, server_default=text("'0'"))

    seq_region = relationship("SeqRegion", primaryjoin="MiscFeature.seq_region_id == SeqRegion.seq_region_id")
    # misc_sets = relationship("MiscSet", secondary=t_misc_feature_misc_set)


class ObjectXref(Base):
    __tablename__ = "object_xref"
    __table_args__ = (
        Index("ensembl_idx", "ensembl_object_type", "ensembl_id"),
        Index(
            "xref_idx",
            "xref_id",
            "ensembl_object_type",
            "ensembl_id",
            "analysis_id",
            unique=True,
        ),
    )

    object_xref_id: Column = Column(INTEGER(10), primary_key=True)
    ensembl_id: Column = Column(INTEGER(10), nullable=False)
    ensembl_object_type: Column = Column(
        Enum(
            "RawContig",
            "Transcript",
            "Gene",
            "Translation",
            "Operon",
            "OperonTranscript",
            "Marker",
            "RNAProduct",
        ),
        nullable=False,
    )
    xref_id: Column = Column(ForeignKey("xref.xref_id"), nullable=False)
    linkage_annotation: Column = Column(String(255))
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        index=True,
    )

    analysis = relationship("Analysis", primaryjoin="ObjectXref.analysis_id == Analysis.analysis_id")
    xref = relationship("Xref", primaryjoin="ObjectXref.xref_id == Xref.xref_id")


class DependentXref(ObjectXref):
    __tablename__ = "dependent_xref"

    object_xref_id: Column = Column(
        ForeignKey("object_xref.object_xref_id"),
        primary_key=True,
    )
    master_xref_id: Column = Column(
        ForeignKey("xref.xref_id"),
        nullable=False,
        index=True,
    )
    dependent_xref_id: Column = Column(
        ForeignKey("xref.xref_id"),
        nullable=False,
        index=True,
    )


class IdentityXref(ObjectXref):
    __tablename__ = "identity_xref"

    object_xref_id: Column = Column(
        ForeignKey("object_xref.object_xref_id"),
        primary_key=True,
    )
    xref_identity: Column = Column(INTEGER(5))
    ensembl_identity: Column = Column(INTEGER(5))
    xref_start: Column = Column(INTEGER(11))
    xref_end: Column = Column(INTEGER(11))
    ensembl_start: Column = Column(INTEGER(11))
    ensembl_end: Column = Column(INTEGER(11))
    cigar_line: Column = Column(Text)
    score: Column = Column(Float(asdecimal=True))
    evalue: Column = Column(Float(asdecimal=True))

    object_xref = relationship(
        "ObjectXref",
        uselist=False,
        primaryjoin="IdentityXref.object_xref_id == ObjectXref.object_xref_id",
    )


class Operon(Base):
    __tablename__ = "operon"
    __table_args__ = (
        Index("operon_seq_region_idx", "seq_region_id", "seq_region_start"),
        Index("operon_stable_id_idx", "stable_id", "version"),
    )

    operon_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(2), nullable=False)
    display_label: Column = Column(String(255), index=True)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    stable_id: Column = Column(String(128))
    version: Column = Column(SMALLINT(5))
    created_date: Column = Column(DateTime)
    modified_date: Column = Column(DateTime)

    analysis = relationship("Analysis", primaryjoin="Operon.analysis_id == Analysis.analysis_id")
    seq_region = relationship("SeqRegion", primaryjoin="Operon.seq_region_id == SeqRegion.seq_region_id")


class PredictionTranscript(Base):
    __tablename__ = "prediction_transcript"
    __table_args__ = (Index("prediction_transcript_seq_region_idx", "seq_region_id", "seq_region_start"),)

    prediction_transcript_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(4), nullable=False)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    display_label: Column = Column(String(255))

    analysis = relationship(
        "Analysis",
        primaryjoin="PredictionTranscript.analysis_id == Analysis.analysis_id",
    )
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="PredictionTranscript.seq_region_id == SeqRegion.seq_region_id",
    )


class ProteinAlignFeature(Base):
    __tablename__ = "protein_align_feature"
    __table_args__ = (
        Index("protein_align_seq_region_idx_2", "seq_region_id", "seq_region_start"),
        Index(
            "seq_region_idx",
            "seq_region_id",
            "analysis_id",
            "seq_region_start",
            "score",
        ),
    )

    protein_align_feature_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    hit_start: Column = Column(INTEGER(10), nullable=False)
    hit_end: Column = Column(INTEGER(10), nullable=False)
    hit_name: Column = Column(String(40), nullable=False, index=True)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    score: Column = Column(Float(asdecimal=True))
    evalue: Column = Column(Float(asdecimal=True))
    perc_ident: Column = Column(Float)
    cigar_line: Column = Column(Text)
    external_db_id: Column = Column(
        ForeignKey("external_db.external_db_id"),
        index=True,
    )
    hcoverage: Column = Column(Float(asdecimal=True))
    align_type: Column = Column(Enum("ensembl", "cigar", "vulgar", "mdtag"), server_default=text("'ensembl'"))

    analysis = relationship(
        "Analysis",
        primaryjoin="ProteinAlignFeature.analysis_id == Analysis.analysis_id",
    )
    external_db = relationship(
        "ExternalDb",
        primaryjoin="ProteinAlignFeature.external_db_id == ExternalDb.external_db_id",
    )
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="ProteinAlignFeature.seq_region_id == SeqRegion.seq_region_id",
    )


class RepeatFeature(Base):
    __tablename__ = "repeat_feature"
    __table_args__ = (Index("repeat_feature_seq_region_idx", "seq_region_id", "seq_region_start"),)

    repeat_feature_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    repeat_start: Column = Column(INTEGER(10), nullable=False)
    repeat_end: Column = Column(INTEGER(10), nullable=False)
    repeat_consensus_id: Column = Column(
        ForeignKey("repeat_consensus.repeat_consensus_id"),
        nullable=False,
        index=True,
    )
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    score: Column = Column(Float(asdecimal=True))

    analysis = relationship("Analysis", primaryjoin="RepeatFeature.analysis_id == Analysis.analysis_id")
    repeat_consensus = relationship(
        "RepeatConsensus",
        primaryjoin="RepeatFeature.repeat_consensus_id == RepeatConsensus.repeat_consensus_id",
    )
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="RepeatFeature.seq_region_id == SeqRegion.seq_region_id",
    )


class SeqRegionAttrib(Base):
    __tablename__ = "seq_region_attrib"
    __table_args__ = (
        Index(
            "region_attribx",
            "seq_region_id",
            "attrib_type_id",
            "value",
            unique=True,
            mysql_length={"value": 10},
        ),
        Index("region_attrib_type_val_idx", "attrib_type_id", "value", mysql_length={"value": 10}),
        Index("region_attrib_value_idx", "value", mysql_length=10),
    )

    seq_region_attrib_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    attrib_type_id: Column = Column(
        ForeignKey("attrib_type.attrib_type_id"),
        nullable=False,
        server_default=text("'0'"),
    )
    value: Column = Column(Text, nullable=False)
    seq_region = relationship("SeqRegion", back_populates="seq_region_attrib")
    attrib_type = relationship("AttribType", back_populates="seq_region_attrib")


# Not in first normal form, can't be mapped (i.e. it has fully duplicated rows for homo_sapiens_core)
t_seq_region_mapping = Table(
    "seq_region_mapping",
    metadata,
    Column("external_seq_region_id", INTEGER(10), nullable=False),
    Column(
        "internal_seq_region_id",
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
        index=True,
    ),
    Column(
        "mapping_set_id",
        ForeignKey("mapping_set.mapping_set_id"),
        nullable=False,
        index=True,
    ),
)


class SeqRegionSynonym(Base):
    __tablename__ = "seq_region_synonym"
    __table_args__ = (Index("syn_idx", "synonym", "seq_region_id", unique=True),)

    seq_region_synonym_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
        index=True,
    )
    synonym: Column = Column(String(250), nullable=False)
    external_db_id: Column = Column(ForeignKey("external_db.external_db_id"))

    seq_region = relationship("SeqRegion", back_populates="seq_region_synonym")
    external_db = relationship("ExternalDb", back_populates="seq_region_synonym")


class SimpleFeature(Base):
    __tablename__ = "simple_feature"
    __table_args__ = (Index("simple_feature_seq_region_idx", "seq_region_id", "seq_region_start"),)

    simple_feature_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(1), nullable=False)
    display_label: Column = Column(String(255), nullable=False, index=True)
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    score: Column = Column(Float(asdecimal=True))

    analysis = relationship("Analysis", primaryjoin="SimpleFeature.analysis_id == Analysis.analysis_id")
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="SimpleFeature.seq_region_id == SeqRegion.seq_region_id",
    )


class AssociatedXref(Base):
    __tablename__ = "associated_xref"
    __table_args__ = (
        Index(
            "object_associated_source_type_idx",
            "object_xref_id",
            "xref_id",
            "source_xref_id",
            "condition_type",
            "associated_group_id",
            unique=True,
        ),
    )

    associated_xref_id: Column = Column(INTEGER(10), primary_key=True)
    object_xref_id: Column = Column(
        ForeignKey("object_xref.object_xref_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    xref_id: Column = Column(
        ForeignKey("xref.xref_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    source_xref_id: Column = Column(INTEGER(10), index=True)
    condition_type: Column = Column(String(128))
    associated_group_id: Column = Column(
        ForeignKey("associated_group.associated_group_id"),
        index=True,
    )
    rank: Column = Column(INTEGER(10), server_default=text("'0'"))

    associated_group = relationship(
        "AssociatedGroup",
        primaryjoin="AssociatedXref.associated_group_id == AssociatedGroup.associated_group_id",
    )
    object_xref = relationship(
        "ObjectXref",
        primaryjoin="AssociatedXref.object_xref_id == ObjectXref.object_xref_id",
    )
    xref = relationship("Xref", primaryjoin="AssociatedXref.xref_id == Xref.xref_id")


class ExonTranscript(Base):
    __tablename__ = "exon_transcript"

    exon_id: Column = Column(
        ForeignKey("exon.exon_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    transcript_id: Column = Column(
        ForeignKey("transcript.transcript_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    rank: Column = Column(INTEGER(10), primary_key=True, nullable=False)

    exon = relationship("Exon", primaryjoin="ExonTranscript.exon_id == Exon.exon_id")
    transcript = relationship(
        "Transcript",
        primaryjoin="ExonTranscript.transcript_id == Transcript.transcript_id",
    )


class MiscAttrib(Base):
    __tablename__ = "misc_attrib"
    __table_args__ = (
        Index("misc_attrib_type_val_idx", "attrib_type_id", "value", mysql_length={"value": 10}),
        Index(
            "misc_attribx",
            "misc_feature_id",
            "attrib_type_id",
            "value",
            unique=True,
            mysql_length={"value": 10},
        ),
        Index("misc_attrib_value_idx", "value", mysql_length=10),
    )

    misc_attrib_id: Column = Column(INTEGER(10), primary_key=True)
    misc_feature_id: Column = Column(
        INTEGER(10),
        ForeignKey("misc_feature.misc_feature_id"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    attrib_type_id: Column = Column(
        SMALLINT(5),
        ForeignKey("attrib_type.attrib_type_id"),
        nullable=False,
        server_default=text("'0'"),
    )
    value: Column = Column(Text, nullable=False)


class OntologyXref(Base):
    __tablename__ = "ontology_xref"
    __table_args__ = (
        Index(
            "object_source_type_idx",
            "object_xref_id",
            "source_xref_id",
            "linkage_type",
            unique=True,
        ),
    )

    object_xref_id: Column = Column(
        INTEGER(10),
        ForeignKey("object_xref.object_xref_id"),
        primary_key=True,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    source_xref_id: Column = Column(
        INTEGER(10),
        ForeignKey("xref.xref_id"),
        primary_key=True,
        index=True,
    )
    linkage_type: Column = Column(String(3), primary_key=True)


class OperonTranscript(Base):
    __tablename__ = "operon_transcript"
    __table_args__ = (
        Index("operon_transcript_stable_id_idx", "stable_id", "version"),
        Index("operon_transcript_seq_region_idx", "seq_region_id", "seq_region_start"),
    )

    operon_transcript_id: Column = Column(INTEGER(10), primary_key=True)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(2), nullable=False)
    operon_id: Column = Column(
        ForeignKey("operon.operon_id"),
        nullable=False,
        index=True,
    )
    display_label: Column = Column(String(255))
    analysis_id: Column = Column(
        ForeignKey("analysis.analysis_id"),
        nullable=False,
        index=True,
    )
    stable_id: Column = Column(String(128))
    version: Column = Column(SMALLINT(5))
    created_date: Column = Column(DateTime)
    modified_date: Column = Column(DateTime)

    analysis = relationship("Analysis", primaryjoin="OperonTranscript.analysis_id == Analysis.analysis_id")
    operon = relationship("Operon", primaryjoin="OperonTranscript.operon_id == Operon.operon_id")
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="OperonTranscript.seq_region_id == SeqRegion.seq_region_id",
    )


class PredictionExon(Base):
    __tablename__ = "prediction_exon"
    __table_args__ = (Index("prediction_exon_seq_region_idx", "seq_region_id", "seq_region_start"),)

    prediction_exon_id: Column = Column(INTEGER(10), primary_key=True)
    prediction_transcript_id: Column = Column(
        ForeignKey("prediction_transcript.prediction_transcript_id"),
        nullable=False,
        index=True,
    )
    exon_rank: Column = Column(SMALLINT(5), nullable=False)
    seq_region_id: Column = Column(
        ForeignKey("seq_region.seq_region_id"),
        nullable=False,
    )
    seq_region_start: Column = Column(INTEGER(10), nullable=False)
    seq_region_end: Column = Column(INTEGER(10), nullable=False)
    seq_region_strand: Column = Column(TINYINT(4), nullable=False)
    start_phase: Column = Column(TINYINT(4), nullable=False)
    score: Column = Column(Float(asdecimal=True))
    p_value: Column = Column(Float(asdecimal=True))

    prediction_transcript = relationship(
        "PredictionTranscript",
        primaryjoin=(
            "PredictionExon.prediction_transcript_id ==" "PredictionTranscript.prediction_transcript_id"
        ),
    )
    seq_region = relationship(
        "SeqRegion",
        primaryjoin="PredictionExon.seq_region_id == SeqRegion.seq_region_id",
    )


class SupportingFeature(Base):
    __tablename__ = "supporting_feature"
    __table_args__ = (
        Index("supporting_feature_all_idx", "exon_id", "feature_type", "feature_id", unique=True),
        Index("supporting_feature_idx", "feature_type", "feature_id"),
    )

    exon_id: Column = Column(
        INTEGER(10),
        ForeignKey("exon.exon_id"),
        primary_key=True,
        nullable=False,
        server_default=text("'0'"),
    )
    feature_type: Column = Column(Enum("dna_align_feature", "protein_align_feature"), primary_key=True)
    feature_id: Column = Column(INTEGER(10), primary_key=True, nullable=False, server_default=text("'0'"))


t_operon_transcript_gene = Table(
    "operon_transcript_gene",
    metadata,
    Column(
        "operon_transcript_id",
        ForeignKey("operon_transcript.operon_transcript_id"),
    ),
    Column("gene_id", ForeignKey("gene.gene_id"), index=True),
    Index("operon_transcript_gene_idx", "operon_transcript_id", "gene_id"),
)


@compiles(SET, "sqlite")
def compile_set_sqlite(
    type_: sqlalchemy.sql.expression.ColumnClause,  # pylint: disable=unused-argument
    compiler: sqlalchemy.engine.interfaces.Compiled,  # pylint: disable=unused-argument
    **kw: Any,  # pylint: disable=unused-argument
) -> str:
    """Cast MySQL SET to SQLite TEXT."""
    return "TEXT"


@compiles(TINYTEXT, "sqlite")
def compile_tinytext_sqlite(
    type_: sqlalchemy.sql.expression.ColumnClause,  # pylint: disable=unused-argument
    compiler: sqlalchemy.engine.interfaces.Compiled,  # pylint: disable=unused-argument
    **kw: Any,  # pylint: disable=unused-argument
) -> str:
    """Cast MySQL TINYTEXT to SQLite TEXT."""
    return "TEXT"


@compiles(MEDIUMTEXT, "sqlite")
def compile_mediumtext_sqlite(
    type_: sqlalchemy.sql.expression.ColumnClause,  # pylint: disable=unused-argument
    compiler: sqlalchemy.engine.interfaces.Compiled,  # pylint: disable=unused-argument
    **kw: Any,  # pylint: disable=unused-argument
) -> str:
    """Cast MySQL MEDIUMTEXT to SQLite TEXT."""
    return "TEXT"


@compiles(LONGTEXT, "sqlite")
def compile_longtext_sqlite(
    type_: sqlalchemy.sql.expression.ColumnClause,  # pylint: disable=unused-argument
    compiler: sqlalchemy.engine.interfaces.Compiled,  # pylint: disable=unused-argument
    **kw: Any,  # pylint: disable=unused-argument
) -> str:
    """Cast MySQL LONGTEXT to SQLite TEXT."""
    return "TEXT"


@compiles(TINYINT, "sqlite")
def compile_tinyint_sqlite(
    type_: sqlalchemy.sql.expression.ColumnClause,  # pylint: disable=unused-argument
    compiler: sqlalchemy.engine.interfaces.Compiled,  # pylint: disable=unused-argument
    **kw: Any,  # pylint: disable=unused-argument
) -> str:
    """Cast MySQL TINYINT to SQLite INT."""
    return "INT"


@compiles(DOUBLE, "sqlite")
def compile_double_sqlite(
    type_: sqlalchemy.sql.expression.ColumnClause,  # pylint: disable=unused-argument
    compiler: sqlalchemy.engine.interfaces.Compiled,  # pylint: disable=unused-argument
    **kw: Any,  # pylint: disable=unused-argument
) -> str:
    """Cast MySQL DOUBLE to SQLite NUMBER."""
    return "NUMBER"
