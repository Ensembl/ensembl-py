# Ensembl Python Base Library

[![GitHub license](https://img.shields.io/github/license/Ensembl/ensembl-py)](https://github.com/Ensembl/ensembl-py/blob/main/LICENSE)
[![coverage report](https://jalvarez.gitdocs.ebi.ac.uk/ensembl-py/coverage-badge.svg)](https://jalvarez.gitdocs.ebi.ac.uk/ensembl-py/)
[![Documentation deploy](https://github.com/Ensembl/ensembl-py/actions/workflows/documentation.yml/badge.svg)](https://ensembl.github.io/ensembl-py)

Centralise generic Python code use across all other project within Ensembl, more particularly database access layers, reusable eHive components, etc.

## Getting Started

### Installing the development environment with `venv`

```
python -m venv <VIRTUAL_ENVIRONMENT_NAME>
source <VIRTUAL_ENVIRONMENT_NAME>/bin/activate
git clone https://github.com/Ensembl/ensembl-py.git
cd ensembl-py
pip install -e .[cicd,dev,docs]
```

### Testing with `pytest`

Run test suite from the root of the repository is as simple as to run:
```
pytest
```

To run tests, calculate and display testing coverage stats:
```
coverage run -m pytest
coverage report -m
```

### Generate documentation via `mkdocs`
```
mkdocs build
```
Open automatically generated documentation page at `site/index.html`.

### Automatic formatting (PEP8 compliance)
```
black --check .
```
Use `--diff` to print a diff of what Black would change, without actually changing the files.

To actually reformat all files in the repository:
```
black .
```

### Linting and type checking
```
pylint src/python/ensembl
pylint --recursive=y src/python/tests
mypy src/python/ensembl
mypy src/python/tests
```
`pylint` will check the code for syntax, name errors and formatting style. `mypy` will use type hints to statically type check the code.

It should be relatively easy (and definitely useful) to integrate both `pylint` and `mypy` in your IDE/Text editor.

## Useful resources

### Python Documentation
- [Official Python Docs](https://docs.python.org/3/)

### Python virtual environments management
- [Python venv](https://docs.python.org/3/library/venv.html)

### Auto-generating documentation
- [mkdocs](https://www.mkdocs.org)

### Linting, type checking and formatting
- [Pylint](https://www.pylint.org/)
- [Mypy](https://mypy.readthedocs.io/en/stable/)
- [Black](https://black.readthedocs.io/en/stable/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

### Testing
- [pytest](https://docs.pytest.org/en/6.2.x/)
- [Coverage](https://coverage.readthedocs.io/)

### CI/CD
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)

### Development tools
- [IPython](https://ipython.org/)

### Distributing
- [Packaging Python](https://packaging.python.org/tutorials/packaging-projects/)
- [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0#apply)
- [Semantic Versioning](https://semver.org/)
