# See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Unit testing of :mod:`utils.rloader` module.

Typical usage example::

    $ pytest test_rloader.py

"""

import pytest
import requests.exceptions

from ensembl.utils.rloader import RemoteFileLoader


class TestRemoteFileLoader:
    """Tests `ensembl.utils.rloader.RemoteFileLoader`"""

    def test_yaml_load(self):
        """Tests `r_open()` with YAML file"""
        loader = RemoteFileLoader("yaml")
        content = loader.r_open(
            (
                "https://raw.githubusercontent.com/Ensembl/ensembl-py/main/src/python/tests/utils/"
                "test_rloader/sample.yml"
            )
        )
        assert "language" in content
        assert "os" in content

    def test_json_load(self):
        """Tests `r_open()` with JSON file"""
        loader = RemoteFileLoader("json")
        content = loader.r_open(
            "https://raw.githubusercontent.com/Ensembl/ensembl-production/main/modules/t/genes_test.json"
        )
        assert "homologues" in content[0]
        assert "seq_region_synonyms" in content[0]

    def test_ini_load(self):
        """Tests `r_open()` with INI file"""
        loader = RemoteFileLoader("ini")
        content = loader.r_open(
            "https://raw.githubusercontent.com/Ensembl/ensembl-production-services/main/.env.dist"
        )
        assert content.get("DEFAULT", "SECRET_KEY") == "thisisasecretkeynotmeantforproduction"

    def test_env_load(self):
        """Tests `r_open()` with ENV file"""
        loader = RemoteFileLoader("env")
        content = loader.r_open(
            "https://raw.githubusercontent.com/Ensembl/ensembl-production-services/main/.env.dist"
        )
        assert content.get("SECRET_KEY") == "thisisasecretkeynotmeantforproduction"
        assert "DATABASE_URL" in content

    def test_not_existing_load(self):
        """Tests `r_open()` when the file does not exist"""
        loader = RemoteFileLoader("env")
        with pytest.raises(requests.exceptions.HTTPError) as e:
            content = loader.r_open("http://httpbin.org/status/404")
            assert e.message == "Loading http://httpbin.org/status/404 received: 404 (Not found)"
            assert content is None

    def test_raw_load(self):
        """Tests `r_open()` with raw file"""
        loader = RemoteFileLoader()
        content = loader.r_open(
            "https://github.com/Ensembl/ensembl-production/blob/release/104/modules/"
            "Bio/EnsEMBL/Production/Utils/CopyDatabase.pm"
        )
        assert content is not None
        assert "Bio::EnsEMBL::Production::Utils::CopyDatabase" in content
