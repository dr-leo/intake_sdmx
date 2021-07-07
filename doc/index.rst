Statistical Data and Metadata eXchange (SDMX) for the  Python data  ecosystem
********************************************************************************

:mod:`intake_sdmx` is an Apache 2.0-licensed plugin 
for `intake <https://intake.readthedocs.io>`_. It leverages 
`pandaSDMX <https://pandasdmx.readthedocs.io>`_ to bring `SDMX <http://www.sdmx.org>`_ 2.1-formated data and metadata, into the intake data acquisition, distribution and visualization ecosystem.
 

:mod:`intake_sdmx` can be used to:

- explore the dataflows  from about 20 :doc:`data providers <sources>` such as the World Bank, BIS, ILO, ECB,  
  Eurostat, OECD, UNICEF and United Nations through the intake API and GUI;
- export data sets as pandas Series or DataFrame
- expose virtually all pandaSDMX features through the convenient intake API 
- store and distribute metadata packages on   data sets  as declarative YAML or conda packages  

…and much more.

Get started
===========

Assuming  a working copy of `Python 3.7 or higher <https://www.python.org/downloads/>`_ 
is installed on your system,
you can get :mod:`intake_sdmx` either   by typing from the  command prompt::

    $ pip install intake_sdmx

or from a `conda environment <https://www.anaconda.com/>`_::

    $ conda install intake_sdmx -c conda-forge     

Next, look at a
:doc:`usage example in only 10 lines of code <example>`. Then dive into the longer, narrative :doc:`tutorial <tutorial>` and finally peruse   the more advanced chapters as needed.

.. toctree::
   :maxdepth: 1

   example
   tutorial


:mod:`intake_sdmx` user guide
===========================

.. toctree::
   :maxdepth: 2

   tutorial
   api
   whatsnew
   roadmap
   license


Contributing to intake_sdmx and getting help
==========================================

- Report bugs, suggest features or view the source code on
  `GitHub <https://github.com/dr-leo/intake_sdmx>`_.
- The `sdmx-python <https://groups.google.com/forum/?hl=en#!forum/sdmx-python>`_ Google Group and mailing list may have answers for some questions.

- :ref:`genindex`
