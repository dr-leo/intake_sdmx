Installation
============

Required dependencies
---------------------

**intake_sdmx** is a pure `Python <https://python.org>`_ package requiring Python 3.7 or higher,    see `the Python website <https://www.python.org/downloads/>`_. 
It is  recommended to use a scientific Python distribution such as 
  `Anaconda <https://store.continuum.io/cshop/anaconda/>`_.
  
**intake_sdmx** also depends on:

- `pandaSDMX <http://pandasdmx.readthedocs.io>`_ to retrieve and process SDMX data and metadata,
- `intake <https://intake.readthedocs.io>`_ as the overarching framework 
  for data acquisition, distribution and visualisation.

Optional dependencies for extra features
----------------------------------------

- for ``doc``, to build the documentation: `sphinx <https://sphinx-doc.org>`_
  and `IPython <https://ipython.org>`_.
- for ``test``, to run the test suite: `pytest <https://pytest.org>`_,
  `requests-mock <https://requests-mock.readthedocs.io>`_.

Instructions
------------

0. (optional) If using a `conda environment
   <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_, 
   use ``source activate [ENV]`` to
   activate the
   environment in which to install pandaSDMX.
1. From the command line, issue::

     $ conda install intake_sdmx -c intake     
   
   or optionally from the Python package index::

     $ pip install intake_sdmx  

From source
~~~~~~~~~~~

1. Download the latest code:

   - `from PyPI <https://pypi.org/project/intake_sdmx/#files>`_,
   - `from Github <https://github.com/dr-leo/intake_sdmx>`_ as a zip archive, or
   - by cloning the Github repository::

     $ git clone git@github.com:dr-leo/intake_sdmx.git

2. In the package directory, issue::

     $ pip install  .

   or::

      $ flit install
    
.. note:: The build process adheres to 
   `PEP 517 <https://www.python.org/dev/peps/pep-0517/>`_
   using `flit <https://flit.readthedocs.io/en/latest/>`_ as build backend.  

