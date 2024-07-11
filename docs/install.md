# How to install this repository

This Python library only requires Python 3.10+ to work. However, it is likely most functionalities and modules will still be Python 3.9 compatible.

## Basic installation

To install it, just run the following command:

```bash
pip3 install git+https://github.com/Ensembl/ensembl-py.git
```

## Development-oriented installation

To perform a development installation it is advised to use a [Python virtual environment](https://docs.python.org/3/library/venv.html)
(and activate it):

```bash
python3 -m venv path/to/virtual_env
source path/to/virtual_env/bin/activate
```

And then clone the GitHub repository and install it in edit mode:

```bash
git clone https://github.com/Ensembl/ensembl-py.git
pip3 install -e ensembl-py/.[cicd,dev,docs]
```

Documentation generated using _mkdocs_. For full information visit [mkdocs.org](https://www.mkdocs.org).
