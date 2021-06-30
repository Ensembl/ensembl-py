#!/bin/bash

sphinx-apidoc -o docs src/python
cd docs
make html
