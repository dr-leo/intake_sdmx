User Guide
***************



.. contents::
   :local:
   :backlinks: none



Overview
==========

**intake_sdmx** is a plugin for
`intake <https://intake.readthedocs.io/en/latest/>`_
which leverages `pandaSDMX <https://pandasdmx.readthedocs.io/en/latest/>`_
to make data and metadata from  the
`SDMX <https://www.sdmx.org/>`_ ecosystem
accessible via  **intake**. To achieve this,
**intake_sdmx** provides three intake
`drivers <https://intake.readthedocs.io/en/latest/glossary.html#term-Driver>`_:

* :class:`intake_sdmx.SDMXSources`:  a
  `catalog <https://intake.readthedocs.io/en/latest/glossary.html#term-Catalog>`_
  of SDMX data sources
  (a.k.a. agencies or data providers) such as
  national statistics offices, central banks and international institutions
* :class:`intake_sdmx.SDMXDataflows`: a catalog
  of  dataflows provided by a given SDMX data source
* :class:`intake_sdmx.SDMXData`: a
  `data-set <https://intake.readthedocs.io/en/latest/glossary.html#term-Data-set>`_
  that can download data-sets of a specified dataflow
  and convert it to a :class:`pandas.DataFrame`.

Whether you are familiar with **intake**
or **pandaSDMX**,
the above concepts should ring a bell. However, if you are new to both ecosystems,
just read on, follow the code examples,
and dig deeper as needed by skimming
the docs of either **intake** or **pandaSDMX** as needed.

The following sections expand on the  
introductory `code example <https://pandasdmx.readthedocs.io/en/v1.0/example.html>`_
from the pandaSDMX documentation.      

Exploring  the available data sources
======================================

You can instantiate the catalog of
SDMX data sources in one of two ways:

.. ipython:: python

    # firstly, via intake_sdmx:
    from intake_sdmx import *
    src = SDMXSources()
    type(src)
    # secondly, via the intake API:
    import intake
    src2 = intake.open_sdmx_sources()
    # YAML representation
    print(src.yaml())
    src.yaml() == src2.yaml()
    # Available data sources
    list(src)

Two observations:

* For intake-novices: each driver instance can create a
  declarative YAML description of itself which  suffices   to re-generate
  clones by calling :func:`intake.open_yaml`.
* For pandaSDMX-novices: The catalog contains two copies of each data
  provider entry accessible via its ID and name
  (in SDMX terminology)
  respectively. The duplicate entries are a pragmatic response to the
  fact that catalog entries are expensive to instantiate
  as each one requires a HTTP request to a different SDMX web service.
  And dict keys are just fine to show
  human-readable descriptions alongside the IDs.

As in  pandasdmx, you can configure your HTTP connections: 

.. ipython:: python

    src_via_proxy = SDMXSources(
        storage_options={'proxies': {'http': 'http://1.1.1.1:4567'}})

The `storage_options` argument is an **intake** feature. Options will be propagated to
any HTTP connection established by instances derived from `src_via_proxy`. Note that upon instantiation of:class:`SDMXSources` no HTTP connection is made.
        
        
Exploring the dataflows of a given data source
================================================

Suppose we want to analyze annual unemployment data 
for some EU countries. We assume such data to be available from Eurostat.

.. ipython:: python

    estat_flows = src.ESTAT
    type(estat_flows)
    print(estat_flows.yaml())
    len(estat_flows)
    # Wow! 
    list(estat_flows)[:20]

Luckily, this class has a rudimentary :meth:`intake_sdmx.SDMXDataflows.search` method
generating a shorter subcatalog:

.. ipython:: python

    unemployment_flows = estat_flows.search("unemployment")
    len(unemployment_flows)
    # This is still too large... 
    # So let's refine our search.
    unemployment_flows = estat_flows.search("annual unemployment", operator="&")
    list(unemployment_flows)

Note that an intake catalog is essentially a dict. 
In our case, it is noteworthy that while the keys of the above catalog are already populated by IDs and names of the dataflow definitions, the corresponding values 
are None. This is for performance, as instantiating 
a catalog entry and populating it with all 
the metadata associated with an SDMX Dataflow
is expensive. Therefore, **intake_sdmx** uses a :class:`intake_sdmx.LazyDict` under the hood. 
Each value is None until it is accessed.

.. caution:: Avoid iterating over all values of a large  catalog of dataflows 
    as this could take forever.

While with pandaSDMX, you would have performed these searches in a pandas DataFrame, a catalog cannot be exported to a DataFrame. Well, you can convert a list of dataflow names to aboveDataFrame in a single line and do more sophisticated filtering. 
Anyway, we choose `une_rt_a` for further analysis.


Exploring the data structure  
==============================

As most pandaSDMX users will know, each dataflow references a data structure definition (DSD). It contains 
descriptions of dimensions, codelists etc.
One of the most powerful features of SDMX and pandaSDMX is the ability to select subsets of the available data by specifying a so-called key mapping 
dimension names to codes selected from the codelist 
referenced by a given dimension. 
**intake_sdmx** translates dimensions and codelists to 
user-parameters of a catalog entry for a chosen dataflow. Allowed values ofthese parameters are populated with the allowed codes. **intake** thus gives you argument validation for free.

.. ipython:: python

    # Download the complete structural metadata on our
    # 'une_rt_a' dataflow
    une = unemployment_flows.une_rt_a
    type(une)
    print( une.yaml())
    
Two observations:

* The :class:`intake_sdmx.SDMXData` instance knows about the dimensions 
  of the dataflow on annual unemployment data. 
  This information has been extracted from the referenced 
  DatastructureDefinition - a core concept of SDMX.
* All dimensions are wildcarded ("*"). Thus, if we asked the server
  to send us the corresponding dataset, we would probably exceed the server limits, 
  or at least obtain a bunch of data we are not interested in.
  So let's try to select some interesting columns for our data query. 
  
Not only do we have the dimension names. 
We also have all the allowed codes, namely in the 
catalog entry "une_rt_a" from which we have created our instance:

.. ipython:: python

        print(str(une.entry))
        # select some countries 
        # and the startPeriod to restrict our query
        une = une(GEO=['IE', 'ES', 'EL'], startPeriod="2007")
        # Note the new config values
        print(une.yaml())
        # Passed Codes are validated against the codelists:
        try:
            invalid = une(FREQ=['XXX']) 
        except ValueError as e:
            print(e)
        
Note that when deriving a new instance from an exiting one,
the entire configuration is propagated, except for those values we overwrite 
by passing new arguments.
        
Downloading and analyzing data
==================================

**intake_sdmx** can export datasets as pandas Series (default) or DataFrames.
A Series is preferrable, in particular, when you aren't sure 
about the periodicity of the data, as DataFrames requires columns to have consistent datetime indices. 
We shall export our annual unemployment data 
as a DataFrame. To do this, we 
configure our :class:`intake_sdmx.SDMXData` instance 
as follows:

.. ipython:: python

    # configure for DataFrame with PeriodIndex
    une = une(index_type='period')
    # Now download the dataset and export it as DataFrame:
    df = une.read()
    df.loc[:, ('Y15-74', 'PC_ACT', 'T')]
    

    
