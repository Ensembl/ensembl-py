# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Sphinx configuration for the ensembl-py documentation.

All shared defaults live in :mod:`ensembl.utils.docs`; this file only sets project-specific values and any
local overrides.
"""

from pathlib import Path

from ensembl.utils.docs import configure

coverage_root = Path(__file__).parent / "reports"
configure(
    globals(),
    project="ensembl-py",
    repo_url="https://github.com/Ensembl/ensembl-py",
    release="3.1.0",
    docs_base_url="https://ensembl.github.io/ensembl-py",
    coverage_root=coverage_root if coverage_root.exists() else None,
    add_pypi_icon=True,
)
