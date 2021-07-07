Ten-line usage example
======================

The following example is inspired by the pandaSDMX docs, but adapted to the intake API.
Suppose we want to analyze annual unemployment data for some European countries.
All we need to know in advance is the data provider: Eurostat.

intake's  catalog framework
makes it easy to search the directory of dataflows, and the complete structural metadata about the datasets available through the selected dataflow.
(This example skips these steps; see :doc:`the tutorial <tutorial>`.)

The data we want is in a *data flow* with the identifier ``une_rt_a``.


.. ipython:: python

    import intake
    src = intake.open_sdmx()
    list(src) # list of data providers
    estat = src.ESTAT 

Download the metadata:

.. ipython:: python

    unemployment = estat.une_rt_a

Explore the contents of some code lists:

.. ipython:: python

    unemployment.yaml()[:1000]


Next we download a dataset.
To obtain data on Greece, Ireland and Spain only, we use codes from the code list 'CL_GEO' to specify a *key* for the dimension named ‘GEO’.
We also use a query *parameter*, 'startPeriod', to limit the scope of the data returned:

.. ipython:: python

    unemployment_ireland = unemployment(
        GEO='IE',
        startPeriod='2007'
        )

``resp`` is  a :class:`.DataMessage` object.
We use its :meth:`~pandasdmx.message.Message.to_pandas` method to convert it to a :class:`pandas.DataFrame`, and select on the ``AGE`` dimension we saw   in the ``metadata`` above:

.. ipython:: python

    data = unemployment_ireland.read(
        index_type='period').xs('Y15-74', level='AGE') 

We can now explore the data set as expressed in a familiar pandas object.
First, show dimension names:

.. ipython:: python

    data.columns.names

…and corresponding key values along these dimensions:

.. ipython:: python

    data.columns.levels

Select some data of interest: show aggregate unemployment rates across ages ('Y15-74' on the ``AGE`` dimension) and sexes ('T' on the ``SEX`` dimension), expressed as a percentage of active population ('PC_ACT' on the ``UNIT`` dimension):

.. ipython:: python

    data.loc[:, ('Y15-74', 'PC_ACT', 'T')]
