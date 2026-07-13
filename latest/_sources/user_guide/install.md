# Installation

This Python library only requires Python 3.10+ to work. Earlier Python versions are not supported.

## Basic installation

This library is publicly available in [PyPI](https://pypi.org/project/ensembl-py/) so it can be easily installed with your favourite Python dependency and packaging management tool, e.g.

```bash
pip install ensembl-py
```

## Development-oriented installation

If you want to install this library in editable mode, we suggest you to do so via Python's virtual environment module ([venv](https://docs.python.org/3/library/venv.html)):

```bash
python -m venv <VIRTUAL_ENVIRONMENT_NAME>
source <VIRTUAL_ENVIRONMENT_NAME>/bin/activate
git clone https://github.com/Ensembl/ensembl-py.git
cd ensembl-py
pip install -e .[cicd]
```
