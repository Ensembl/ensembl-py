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
"""Unit testing of :mod:`ncbi_taxonomy` module.

Typical usage example::

    $ pytest test_ncbi_taxonomy.py

"""

from typing import ContextManager

import pytest
from pytest import raises
from sqlalchemy.exc import  NoResultFound

from ensembl.database import UnitTestDB
from ensembl.ncbi_taxonomy.api.utils import Taxonomy
from ensembl.ncbi_taxonomy.models import NCBITaxonomy


@pytest.mark.parametrize("db", [{"src": "ncbi_db"}], indirect=True)
class TestNCBITaxonomyUtils:
    """Tests :class:`~ensembl.ncbi_taxonomy.api.utils.Taxonomy` in utils.py"""

    dbc = None  # type: UnitTestDB

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, db: UnitTestDB) -> None:
        """Loads the required fixtures and values as class attributes.

        Args:
            db: Generator of unit test database (fixture).
        """
        type(self).dbc = db.dbc

    result_dict = {
        "taxon_id": 9615,
        "name": "beagle dog",
        "name_class": "includes",
        "parent_id": 9612,
        "rank": "subspecies",
        "genbank_hidden_flag": 1,
        "left_index": 595,
        "right_index": 596,
        "root_id": 1,
    }

    @pytest.mark.parametrize("taxon_id, expectation", [(9615, result_dict)])
    def test_fetch_node_by_id(self, taxon_id: int, expectation: NCBITaxonomy) -> None:
        """Tests :func:`fetch_node_by_id()`

        Args:
            taxon_id: An existing taxon_id as in ncbi_taxonomy.
            expectation: NCBITaxonomy object.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.fetch_node_by_id(session, taxon_id)
            result = result.__dict__
            result.pop("_sa_instance_state")
            assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(9616, raises(NoResultFound))])
    def test_fetch_node_by_id_false_id(
        self, taxon_id: int, expectation: ContextManager
    ) -> None:
        """Tests :func:`fetch_node_by_id()` with a non-existant taxon_id.

        Args:
            taxon_id: A taxon_id that is not in ncbi_taxonomy.
            expectation: NoResultFound() exception.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                result = Taxonomy.fetch_node_by_id(session, taxon_id)
                assert result == expectation

    result_dict2 = {
        "taxon_id": 9615,
        "name": "Canis lupus familiaris",
        "name_class": "scientific name",
        "parent_id": 9612,
        "rank": "subspecies",
        "genbank_hidden_flag": 1,
        "left_index": 595,
        "right_index": 596,
        "root_id": 1,
    }

    @pytest.mark.parametrize(
        "name, expectation", [("Canis lupus familiaris", result_dict2)]
    )
    def test_fetch_taxon_by_species_name(
        self, name: int, expectation: NCBITaxonomy
    ) -> None:
        """Tests :func:`fetch_taxon_by_species_name()`.

        Args:
            name: An existing scientific name as in ncbi_taxonomy.
            expectation: Class NCBITaxonomy object.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.fetch_taxon_by_species_name(session, name)
            result = result.__dict__
            result.pop("_sa_instance_state")
            assert result == expectation

    @pytest.mark.parametrize(
        "name, expectation", [("Canis loopy familiaris", raises(NoResultFound))]
    )
    def test_fetch_taxon_by_species_name_false_name(
        self, name: int, expectation: ContextManager
    ) -> None:
        """Tests :func:`fetch_taxon_by_species_name()` with a non-existant name.

        Args:
            name: A false scientific name not in ncbi_taxonomy.
            expectation: NoResultFound() exception.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                result = Taxonomy.fetch_taxon_by_species_name(session, name)
                assert result == expectation

    result_dict3 = {
        "taxon_id": 9612,
        "name": "Canis lupus",
        "name_class": "scientific name",
        "parent_id": 9611,
        "rank": "species",
        "genbank_hidden_flag": 1,
        "left_index": 594,
        "right_index": 597,
        "root_id": 1,
    }

    @pytest.mark.parametrize("taxon_id, expectation", [(9615, result_dict3)])
    def test_parent(self, taxon_id: int, expectation: NCBITaxonomy) -> None:
        """Tests :func:`parent()`.

        Args:
            taxon_id: An existing taxon_id as in ncbi_taxonomy.
            expectation: Class NCBITaxonomy object.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.parent(session, taxon_id)
            result = result.__dict__
            result.pop("_sa_instance_state")
            assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(9616, raises(NoResultFound))])
    def test_parent_false_id(self, taxon_id: int, expectation: ContextManager) -> None:
        """Tests :func:`parent()` with non-existant taxon_id.

        Args:
            taxon_id: A false taxon_id not in ncbi_taxonomy.
            expectation: NoResultFound() exception.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                result = Taxonomy.parent(session, taxon_id)
                assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(1, raises(NoResultFound))])
    def test_parent_as_root_id(
        self, taxon_id: int, expectation: ContextManager
    ) -> None:
        """Tests :func:`parent()` with root taxon_id, no parent expected of course.

        Args:
            taxon_id: The root taxon_id not in ncbi_taxonomy.
            expectation: NoResultFound() exception.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                result = Taxonomy.parent(session, taxon_id)
                assert result == expectation

    result_tuple = (
        {
            "genbank_hidden_flag": 0,
            "left_index": 356,
            "name": "Hystricognathi",
            "name_class": "scientific name",
            "parent_id": 9989,
            "rank": "suborder",
            "right_index": 363,
            "root_id": 1,
            "taxon_id": 33550,
        },
        {
            "genbank_hidden_flag": 0,
            "left_index": 364,
            "name": "Sciurognathi",
            "name_class": "scientific name",
            "parent_id": 9989,
            "rank": "suborder",
            "right_index": 399,
            "root_id": 1,
            "taxon_id": 33553,
        },
    )

    @pytest.mark.parametrize("taxon_id, expectation", [(9989, result_tuple)])
    def test_children(self, taxon_id: int, expectation: tuple) -> None:
        """Tests :func:`children()`.

        Args:
            taxon_id: An existing taxon_id as in ncbi_taxonomy.
            expectation: A tuple of Class NCBITaxonomy objects.
        """
        with self.dbc.session_scope() as session:
            results = Taxonomy.children(session, taxon_id)
            rows = list(results)
            for row in rows:
                row.pop("_sa_instance_state")
            results = tuple(rows)
            assert results == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(9615, raises(NoResultFound))])
    def test_children_none(self, taxon_id: int, expectation: ContextManager) -> None:
        """Tests :func:`children()` with extant leaf taxon_id, no children expected of course.

        Args:
            taxon_id: The root taxon_id not in ncbi_taxonomy.
            expectation: NoResultFound() exception.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                results = Taxonomy.children(session, taxon_id)
                assert results == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(1, True)])
    def test_is_root(self, taxon_id: int, expectation: bool) -> None:
        """Tests :func:`is_root()`.

        Args:
            taxon_id: Root taxon_id as in ncbi_taxonomy.
            expectation: True.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.is_root(session, taxon_id)
            assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(9615, False)])
    def test_is_root_not_root(self, taxon_id: int, expectation: bool) -> None:
        """Tests :func:`is_root()` with extant leaf taxon_id, not a root.

        Args:
            taxon_id: A leaf taxon_id in ncbi_taxonomy.
            expectation: False.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.is_root(session, taxon_id)
            assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(9612, 1)])
    def test_num_descendants(self, taxon_id: int, expectation: int) -> None:
        """Tests :func:`num_descendants()`.

        Args:
            taxon_id: An internal node taxon_id in ncbi_taxonomy.
            expectation: Correct number of descendants.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.num_descendants(session, taxon_id)
            assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(1, 381)])
    def test_num_descendants_large(self, taxon_id: int, expectation: int) -> None:
        """Tests :func:`num_descendants()`.

        Args:
            taxon_id: The root node taxon_id in ncbi_taxonomy.
            expectation: The total number taxon entries in db - 1.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.num_descendants(session, taxon_id)
            assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(9615, 0)])
    def test_num_descendants_leaf_taxon(self, taxon_id: int, expectation: int) -> None:
        """Tests :func:`num_descendants()` with leaf taxon_id.

        Args:
            taxon_id: Leaf taxon_id not in ncbi_taxonomy.
            expectation: Correct number of descendants.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.num_descendants(session, taxon_id)
            assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(0, raises(NoResultFound))])
    def test_num_descendants_false_taxon(
        self, taxon_id: int, expectation: ContextManager
    ) -> None:
        """Tests :func:`num_descendants()` with leaf taxon_id.

        Args:
            taxon_id: Leaf taxon_id not in ncbi_taxonomy.
            expectation: Correct number of descendants.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                result = Taxonomy.num_descendants(session, taxon_id)
                assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(9615, True)])
    def test_is_leaf(self, taxon_id: int, expectation: bool) -> None:
        """Tests :func:`is_leaf()`.

        Args:
            taxon_id: leaf taxon_id as in ncbi_taxonomy.
            expectation: True.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.is_leaf(session, taxon_id)
            assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(1, False)])
    def test_is_leaf_not_leaf(self, taxon_id: int, expectation: bool) -> None:
        """Tests :func:`is_leaf()` with root taxon_id - so not a leaf.

        Args:
            taxon_id: The root taxon_id in ncbi_taxonomy.
            expectation: False.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.is_leaf(session, taxon_id)
            assert result == expectation

    result_tuple2 = (
        {
            'genbank_hidden_flag': 0,
            'left_index': 1,
            'parent_id': 0,
            'rank': 'no rank',
            'right_index': 764,
            'root_id': 1,
            'taxon_id': 1,
        },
        {
            'genbank_hidden_flag': 0,
            'left_index': 3,
            'parent_id': 131567,
            'rank': 'superkingdom',
            'right_index': 762,
            'root_id': 1,
            'taxon_id': 2759,
        },
        {
            'genbank_hidden_flag': 1,
            'left_index': 4,
            'parent_id': 2759,
            'rank': 'no rank',
            'right_index': 761,
            'root_id': 1,
            'taxon_id': 33154,
        },
        {
            'genbank_hidden_flag': 1,
            'left_index': 2,
            'parent_id': 1,
            'rank': 'no rank',
            'right_index': 763,
            'root_id': 1,
            'taxon_id': 131567,
        },
    )

    @pytest.mark.parametrize("taxon_id, expectation", [(33208, result_tuple2)])
    def test_fetch_ancestors(self, taxon_id: int, expectation: tuple) -> None:
        """Tests :func:`fetch_ancestors()`.

        Args:
            taxon_id: An existing taxon_id as in ncbi_taxonomy.
            expectation: A tuple of dictionary from Taxonomy objects.
        """
        with self.dbc.session_scope() as session:
            results = Taxonomy.fetch_ancestors(session, taxon_id)
            rows = list(results)
            for row in rows:
                row.pop("_sa_instance_state")
            results = tuple(rows)
            assert results == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(1, raises(NoResultFound))])
    def test_fetch_ancestors_root(
        self, taxon_id: int, expectation: ContextManager
    ) -> None:
        """Tests :func:`fetch_ancestors()` with root taxon_id.

        Args:
            taxon_id: The root taxon_id as in ncbi_taxonomy.
            expectation: NoResultFound() exception.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                result = Taxonomy.fetch_ancestors(session, taxon_id)
                assert result == expectation

    @pytest.mark.parametrize("taxon_id, expectation", [(0, raises(NoResultFound))])
    def test_fetch_ancestors_false_taxon(
        self, taxon_id: int, expectation: ContextManager
    ) -> None:
        """Tests :func:`fetch_ancestors()` with non-existant taxon_id.

        Args:
            taxon_id: False taxon_id not in ncbi_taxonomy.
            expectation: NoResultFound() exception.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                result = Taxonomy.fetch_ancestors(session, taxon_id)
                assert result == expectation

    result_tuple3 = (
        {
            "genbank_hidden_flag": 0,
            "left_index": 1,
            "name": "all",
            "name_class": "synonym",
            "parent_id": 0,
            "rank": "no rank",
            "right_index": 764,
            "root_id": 1,
            "taxon_id": 1,
        },
        {
            "genbank_hidden_flag": 1,
            "left_index": 2,
            "name": "biota",
            "name_class": "synonym",
            "parent_id": 1,
            "rank": "no rank",
            "right_index": 763,
            "root_id": 1,
            "taxon_id": 131567,
        },
        {
            "genbank_hidden_flag": 0,
            "left_index": 3,
            "name": "Eucarya",
            "name_class": "synonym",
            "parent_id": 131567,
            "rank": "superkingdom",
            "right_index": 762,
            "root_id": 1,
            "taxon_id": 2759,
        },
        {
            "genbank_hidden_flag": 1,
            "left_index": 4,
            "name": "1500",
            "name_class": "ensembl timetree mya",
            "parent_id": 2759,
            "rank": "no rank",
            "right_index": 761,
            "root_id": 1,
            "taxon_id": 33154,
        },
    )

    @pytest.mark.parametrize(
        "taxon_id1, taxon_id2, expectation", [(33208, 4751, result_tuple3)]
    )
    def test_all_common_ancestors(
        self, taxon_id1: int, taxon_id2: int, expectation: tuple
    ) -> None:
        """Tests :func:`all_common_ancestors()`.

        Args:
            taxon_id1: An existing taxon_id as in ncbi_taxonomy.
            taxon_id2: An existing taxon_id as in ncbi_taxonomy.
            expectation: A tuple of Class NCBITaxonomy objects.
        """
        with self.dbc.session_scope() as session:
            results = Taxonomy.all_common_ancestors(session, taxon_id1, taxon_id2)
            rows = list(results)
            result = []
            for row in rows:
                row = row.__dict__
                row.pop("_sa_instance_state")
                result.append(row)
            results = tuple(result)
            assert results == expectation

    @pytest.mark.parametrize(
        "taxon_id1, taxon_id2, expectation", [(1, 9615, raises(NoResultFound))]
    )
    def test_all_common_ancestors_root(
        self, taxon_id1: int, taxon_id2: int, expectation: ContextManager
    ) -> None:
        """Tests :func:`all_common_ancestors()` with leaf taxon_id.

        Args:
            taxon_id1: A root node taxon_id as in ncbi_taxonomy.
            taxon_id2: A taxon_id as in ncbi_taxonomy.
            expectation: NoResultFound() exception.
        """
        with expectation:
            with self.dbc.session_scope() as session:
                result = Taxonomy.all_common_ancestors(session, taxon_id1, taxon_id2)
                assert result == expectation

    result_dict4 = {
        "genbank_hidden_flag": 0,
        "left_index": 1,
        "name": "all",
        "name_class": "synonym",
        "parent_id": 0,
        "rank": "no rank",
        "right_index": 764,
        "root_id": 1,
        "taxon_id": 1,
    }

    @pytest.mark.parametrize(
        "taxon_id1, taxon_id2, expectation", [(33154, 131567, result_dict4)]
    )
    def test_last_common_ancestors(
        self, taxon_id1: int, taxon_id2: int, expectation: tuple
    ) -> None:
        """Tests :func:`all_common_ancestors()`.

        Args:
            taxon_id1: An existing taxon_id as in ncbi_taxonomy.
            taxon_id2: An existing taxon_id as in ncbi_taxonomy.
            expectation: A Class NCBITaxonomy objects.
        """
        with self.dbc.session_scope() as session:
            result = Taxonomy.last_common_ancestor(session, taxon_id1, taxon_id2)
            result = result.__dict__
            result.pop("_sa_instance_state")
            assert result == expectation

