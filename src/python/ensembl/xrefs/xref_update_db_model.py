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
"""Xref Update database ORM."""
# Ignore some pylint and mypy checks due to the nature of SQLAlchemy ORMs
# pylint: disable=missing-class-docstring,too-many-lines
# mypy: disable-error-code="misc, valid-type"

from sqlalchemy import Column, Index, Enum, DateTime, text
from sqlalchemy.dialects.mysql import (
    INTEGER,
    VARCHAR,
    BOOLEAN,
    TEXT,
    MEDIUMTEXT,
    TINYINT,
    CHAR,
    SMALLINT,
    DOUBLE,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Xref(Base):
    __tablename__ = "xref"
    __table_args__ = (
        Index(
            "acession_idx",
            "accession",
            "source_id",
            "species_id",
            "label",
            unique=True,
            mysql_length={"accession": 100, "label": 100},
        ),
        Index("species_source_idx", "species_id", "source_id"),
    )

    xref_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    accession: Column = Column(VARCHAR(255), nullable=False)
    version: Column = Column(INTEGER(10, unsigned=True))
    label: Column = Column(VARCHAR(255))
    description: Column = Column(TEXT)
    source_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    species_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
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
        server_default=text("'NONE'"),
    )
    info_text: Column = Column(VARCHAR(255), nullable=False, server_default=text("''"))
    dumped: Column = Column(
        Enum(
            "MAPPED",
            "NO_DUMP_ANOTHER_PRIORITY",
            "UNMAPPED_NO_MAPPING",
            "UNMAPPED_NO_MASTER",
            "UNMAPPED_MASTER_FAILED",
            "UNMAPPED_NO_STABLE_ID",
            "UNMAPPED_INTERPRO",
        )
    )


class PrimaryXref(Base):
    __tablename__ = "primary_xref"

    xref_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True)
    sequence: Column = Column(MEDIUMTEXT)
    sequence_type: Column = Column(Enum("dna", "peptide"))
    status: Column = Column(Enum("experimental", "predicted"))


class DependentXref(Base):
    __tablename__ = "dependent_xref"

    object_xref_id: Column = Column(INTEGER(10, unsigned=True), index=True)
    master_xref_id: Column = Column(INTEGER(10, unsigned=True), index=True, primary_key=True)
    dependent_xref_id: Column = Column(INTEGER(10, unsigned=True), index=True, primary_key=True)
    linkage_annotation: Column = Column(VARCHAR(255))
    linkage_source_id: Column = Column(INTEGER(10, unsigned=True), nullable=False, primary_key=True)


class Synonym(Base):
    __tablename__ = "synonym"

    xref_id: Column = Column(INTEGER(10, unsigned=True), index=True, primary_key=True)
    synonym: Column = Column(VARCHAR(255), index=True, primary_key=True)


class Source(Base):
    __tablename__ = "source"

    source_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    name: Column = Column(VARCHAR(255), nullable=False, index=True)
    status: Column = Column(
        Enum("KNOWN", "XREF", "PRED", "ORTH", "PSEUDO", "LOWEVIDENCE", "NOIDEA"),
        nullable=False,
        server_default=text("'NOIDEA'"),
    )
    source_release: Column = Column(VARCHAR(255))
    ordered: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    priority: Column = Column(INTEGER(5, unsigned=True), server_default=text("1"))
    priority_description: Column = Column(VARCHAR(40), server_default=text("''"))


class SourceURL(Base):
    __tablename__ = "source_url"

    source_url_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    source_id: Column = Column(INTEGER(10, unsigned=True), nullable=False, index=True)
    species_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    parser: Column = Column(VARCHAR(255))


class GeneDirectXref(Base):
    __tablename__ = "gene_direct_xref"

    general_xref_id: Column = Column(INTEGER(10, unsigned=True), index=True, primary_key=True)
    ensembl_stable_id: Column = Column(VARCHAR(255), index=True, primary_key=True)
    linkage_xref: Column = Column(VARCHAR(255))


class TranscriptDirectXref(Base):
    __tablename__ = "transcript_direct_xref"

    general_xref_id: Column = Column(INTEGER(10, unsigned=True), index=True, primary_key=True)
    ensembl_stable_id: Column = Column(VARCHAR(255), index=True, primary_key=True)
    linkage_xref: Column = Column(VARCHAR(255))


class TranslationDirectXref(Base):
    __tablename__ = "translation_direct_xref"

    general_xref_id: Column = Column(INTEGER(10, unsigned=True), index=True, primary_key=True)
    ensembl_stable_id: Column = Column(VARCHAR(255), index=True, primary_key=True)
    linkage_xref: Column = Column(VARCHAR(255))


class Species(Base):
    __tablename__ = "species"

    species_id: Column = Column(INTEGER(10, unsigned=True), nullable=False, index=True, primary_key=True)
    taxonomy_id: Column = Column(INTEGER(10, unsigned=True), nullable=False, index=True, primary_key=True)
    name: Column = Column(VARCHAR(255), nullable=False, index=True)
    aliases: Column = Column(VARCHAR(255))


class Pairs(Base):
    __tablename__ = "pairs"

    pair_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    source_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    accession1: Column = Column(VARCHAR(255), nullable=False, index=True)
    accession2: Column = Column(VARCHAR(255), nullable=False, index=True)


class CoordinateXref(Base):
    __tablename__ = "coordinate_xref"
    __table_args__ = (
        Index("start_pos_idx", "species_id", "chromosome", "strand", "txStart"),
        Index("end_pos_idx", "species_id", "chromosome", "strand", "txEnd"),
    )

    coord_xref_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    source_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    species_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    accession: Column = Column(VARCHAR(255), nullable=False)
    chromosome: Column = Column(VARCHAR(255), nullable=False)
    strand: Column = Column(TINYINT(2), nullable=False)
    txStart: Column = Column(INTEGER(10), nullable=False)
    txEnd: Column = Column(INTEGER(10), nullable=False)
    cdsStart: Column = Column(INTEGER(10))
    cdsEnd: Column = Column(INTEGER(10))
    exonStarts: Column = Column(TEXT, nullable=False)
    exonEnds: Column = Column(TEXT, nullable=False)


class ChecksumXref(Base):
    __tablename__ = "checksum_xref"
    __table_args__ = (Index("checksum_idx", "checksum", mysql_length=10),)

    checksum_xref_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    source_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    accession: Column = Column(CHAR(14), nullable=False)
    checksum: Column = Column(CHAR(32), nullable=False)


class Mapping(Base):
    __tablename__ = "mapping"

    job_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True)
    type: Column = Column(Enum("dna", "peptide", "UCSC"))
    command_line: Column = Column(TEXT)
    percent_query_cutoff: Column = Column(INTEGER(10, unsigned=True))
    percent_target_cutoff: Column = Column(INTEGER(10, unsigned=True))
    method: Column = Column(VARCHAR(255))
    array_size: Column = Column(INTEGER(10, unsigned=True))


class MappingJobs(Base):
    __tablename__ = "mapping_jobs"

    mapping_job_id: Column = Column(INTEGER(10), primary_key=True, autoincrement=True)
    root_dir: Column = Column(TEXT)
    map_file: Column = Column(VARCHAR(255))
    status: Column = Column(Enum("SUBMITTED", "FAILED", "SUCCESS"))
    out_file: Column = Column(VARCHAR(255))
    err_file: Column = Column(VARCHAR(255))
    array_number: Column = Column(INTEGER(10, unsigned=True))
    job_id: Column = Column(INTEGER(10, unsigned=True))
    failed_reason: Column = Column(VARCHAR(255))
    object_xref_start: Column = Column(INTEGER(10, unsigned=True))
    object_xref_end: Column = Column(INTEGER(10, unsigned=True))


class GeneTranscriptTranslation(Base):
    __tablename__ = "gene_transcript_translation"

    gene_id: Column = Column(INTEGER(10, unsigned=True), nullable=False, index=True)
    transcript_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True)
    translation_id: Column = Column(INTEGER(10, unsigned=True), index=True)


class ProcessStatus(Base):
    __tablename__ = "process_status"

    id: Column = Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    status: Column = Column(
        Enum(
            "xref_created",
            "parsing_started",
            "parsing_finished",
            "alt_alleles_added",
            "xref_fasta_dumped",
            "core_fasta_dumped",
            "core_data_loaded",
            "mapping_submitted",
            "mapping_finished",
            "mapping_processed",
            "direct_xrefs_parsed",
            "prioritys_flagged",
            "processed_pairs",
            "biomart_test_finished",
            "source_level_move_finished",
            "alt_alleles_processed",
            "official_naming_done",
            "checksum_xrefs_started",
            "checksum_xrefs_finished",
            "coordinate_xrefs_started",
            "coordinate_xref_finished",
            "tests_started",
            "tests_failed",
            "tests_finished",
            "core_loaded",
            "display_xref_done",
            "gene_description_done",
        )
    )
    date: Column = Column(DateTime, nullable=False)


class DisplayXrefPriority(Base):
    __tablename__ = "display_xref_priority"

    ensembl_object_type: Column = Column(VARCHAR(100), primary_key=True)
    source_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True)
    priority: Column = Column(SMALLINT(unsigned=True), nullable=False)


class GeneDescPriority(Base):
    __tablename__ = "gene_desc_priority"

    source_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True)
    priority: Column = Column(SMALLINT(unsigned=True), nullable=False)


class AltAllele(Base):
    __tablename__ = "alt_allele"

    alt_allele_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True)
    gene_id: Column = Column(INTEGER(10, unsigned=True), index=True, primary_key=True)
    is_reference: Column = Column(INTEGER(2, unsigned=True), server_default=text("0"))


class GeneStableId(Base):
    __tablename__ = "gene_stable_id"

    internal_id: Column = Column(INTEGER(10, unsigned=True), nullable=False, index=True)
    stable_id: Column = Column(VARCHAR(128), primary_key=True)
    display_xref_id: Column = Column(INTEGER(10, unsigned=True))
    desc_set: Column = Column(INTEGER(10, unsigned=True), server_default=text("0"))


class TranscriptStableId(Base):
    __tablename__ = "transcript_stable_id"

    internal_id: Column = Column(INTEGER(10, unsigned=True), nullable=False, index=True)
    stable_id: Column = Column(VARCHAR(128), primary_key=True)
    display_xref_id: Column = Column(INTEGER(10, unsigned=True))
    biotype: Column = Column(VARCHAR(40), nullable=False)


class TranslationStableId(Base):
    __tablename__ = "translation_stable_id"

    internal_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True)
    stable_id: Column = Column(VARCHAR(128), nullable=False, index=True)


class ObjectXref(Base):
    __tablename__ = "object_xref"
    __table_args__ = (
        Index(
            "unique_idx",
            "ensembl_object_type",
            "ensembl_id",
            "xref_id",
            "ox_status",
            "master_xref_id",
            unique=True,
        ),
        Index("oxref_idx", "object_xref_id", "xref_id", "ensembl_object_type", "ensembl_id"),
        Index("xref_idx", "xref_id", "ensembl_object_type"),
    )

    object_xref_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    ensembl_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    ensembl_object_type: Column = Column(
        Enum("RawContig", "Transcript", "Gene", "Translation"), nullable=False
    )
    xref_id: Column = Column(INTEGER(10, unsigned=True), nullable=False)
    linkage_annotation: Column = Column(VARCHAR(255))
    linkage_type: Column = Column(
        Enum(
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
        )
    )
    ox_status: Column = Column(
        Enum("DUMP_OUT", "FAILED_PRIORITY", "FAILED_CUTOFF", "NO_DISPLAY", "MULTI_DELETE"),
        nullable=False,
        server_default=text("'DUMP_OUT'"),
    )
    unused_priority: Column = Column(INTEGER(10, unsigned=True))
    master_xref_id: Column = Column(INTEGER(10, unsigned=True))


class IdentityXref(Base):
    __tablename__ = "identity_xref"

    object_xref_id: Column = Column(INTEGER(10, unsigned=True), primary_key=True)
    query_identity: Column = Column(INTEGER(5))
    target_identity: Column = Column(INTEGER(5))
    hit_start: Column = Column(INTEGER(10))
    hit_end: Column = Column(INTEGER(10))
    translation_start: Column = Column(INTEGER(10))
    translation_end: Column = Column(INTEGER(10))
    cigar_line: Column = Column(TEXT)
    score: Column = Column(DOUBLE)
    evalue: Column = Column(DOUBLE)


class Meta(Base):
    __tablename__ = "meta"
    __table_args__ = (
        Index("species_key_value_idx", "meta_id", "species_id", "meta_key", "meta_value", unique=True),
        Index("species_value_idx", "species_id", "meta_value"),
    )

    meta_id: Column = Column(INTEGER(10), primary_key=True, autoincrement=True)
    species_id: Column = Column(INTEGER(10, unsigned=True), server_default=text("1"))
    meta_key: Column = Column(VARCHAR(40), nullable=False)
    meta_value: Column = Column(VARCHAR(255, binary=True), nullable=False)
    date: Column = Column(DateTime, nullable=False)
