.. image:: https://github.com/IDR/idr-py/workflows/Tox/badge.svg
   :target: https://github.com/IDR/idr-py/actions

.. image:: https://badge.fury.io/py/idr-py.svg
    :target: https://badge.fury.io/py/idr-py

IDR-PY
======

Library with helper methods for accessing the Image Data Resource (IDR).

Requirements
============

* OMERO.py 5.6.x
* Python 3.6+

Installing with conda
=====================

This requires `Anaconda/Miniconda with Python 3.6 <https://conda.io/docs/user-guide/install/download.html>`_.

::

    conda env create -f environment.yml -n idr-omero
    conda activate idr-omero


Installing from PyPI
====================

This section assumes that an OMERO.web is already installed.


Install the app using `pip <https://pip.pypa.io/en/stable/>`_:

::

    $ pip install -U idr-py


License
-------

This project, similar to many Open Microscopy Environment (OME) projects, is licensed under the terms of the GNU General Public License (GPL) v2 or later.

Copyright
---------

2017, The Open Microscopy Environment
