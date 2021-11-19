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

import unittest

from ensembl.utils.rloader import RemoteFileLoader


class TestRemoteFileLoader(unittest.TestCase):

    def test_yaml_load(self):
        loader = RemoteFileLoader('yaml')
        content = loader.r_open(
            'https://raw.githubusercontent.com/Ensembl/ensembl-production/main/.travis.yml')
        self.assertIn('language', content)
        self.assertIn('services', content)
        self.assertIn('perl', content)

    def test_json_load(self):
        loader = RemoteFileLoader('json')
        content = loader.r_open(
            'https://raw.githubusercontent.com/Ensembl/ensembl-production/main/modules/t/genes_test.json')
        self.assertIn('homologues', content[0])
        self.assertIn('seq_region_synonyms', content[0])

    def test_ini_load(self):
        loader = RemoteFileLoader('ini')
        content = loader.r_open(
            'https://raw.githubusercontent.com/Ensembl/ensembl-production-services/main/.env.dist')
        self.assertEqual(content.get('DEFAULT', 'SECRET_KEY'), 'thisisasecretkeynotmeantforproduction')

    def test_env_load(self):
        loader = RemoteFileLoader('env')
        content = loader.r_open(
            'https://raw.githubusercontent.com/Ensembl/ensembl-production-services/main/.env.dist')
        self.assertEqual(content.get('SECRET_KEY'), 'thisisasecretkeynotmeantforproduction')
        self.assertIn('DATABASE_URL', content)

    def test_not_existing_load(self):
        loader = RemoteFileLoader('env')
        content = loader.r_open('http://httpbin.org/status/404')
        self.assertIsNone(content)

    def test_raw_load(self):
        loader = RemoteFileLoader()
        content = loader.r_open("https://github.com/Ensembl/ensembl-production/blob/release/104/modules/"
                                "Bio/EnsEMBL/Production/Utils/CopyDatabase.pm")
        self.assertIsNotNone(content)
        self.assertIn("Bio::EnsEMBL::Production::Utils::CopyDatabase", content)
