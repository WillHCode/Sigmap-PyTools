Installation
=============

Installing from PyPI
---------------------

The recommended way to install sigmap-pytools is using pip:

.. code-block:: bash

   pip install sigmap-pytools

Installing from source
-----------------------

To install from source:

.. code-block:: bash

   git clone https://github.com/WillHCode/Sigmap-PyTools.git
   cd Sigmap-PyTools/sigmap-pytools
   pip install -e .

Dependencies
------------

sigmap-pytools requires:

* Python >=3.12
* geopandas >=1.1.1
* shapely >=2.1.2
* requests >=2.32.5
* numpy >=2.3.3
* pandas >=2.3.3
* matplotlib

These dependencies are automatically installed when installing from PyPI.

Development installation
------------------------

For development, install with test dependencies:

.. code-block:: bash

   pip install -e .
   pip install -r requirements_test.txt

Verifying installation
-----------------------

After installation, verify that the package can be imported:

.. code-block:: python

   import sigmap.polygeohasher as polygeohasher
   print(polygeohasher.__version__)

