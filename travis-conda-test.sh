#!/bin/sh

set -eu

# https://conda.io/docs/user-guide/tasks/use-conda-with-travis-ci.html#the-travis-yml-file
curl -L https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -o miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a

# Only install dependencies, not idr-py
sed -n '/pip/q;p' environment-idr-omero53.yml > environment-idr-omero53-deps.yml
conda env create -f environment-idr-omero53-deps.yml -n testenv
source activate testenv
python setup.py install
# Disable default matplotlib backend
python -c 'import matplotlib; matplotlib.use("Agg"); import idr'
