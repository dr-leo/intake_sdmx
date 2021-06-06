"""intake plugin for SDMX data sources"""


import intake
from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry, UserParameter
import pandasdmx as sdmx
from collections.abc import MutableMapping
from datetime import date

__version__ = "0.0.3"

class LazyDict(MutableMapping):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._dict = dict(*args, **kwargs)
        self._func = func

    def __getitem__(self, key):
        if self._dict[key] is None:
            self._dict[key] = self._func(key)
        return self._dict[key]

    def __setitem__(self, key, value):
        return self._dict.__setitem__(key, value)

    def __len__(self):
        return self._dict.__len__()

    def __delitem__(self, key):
        return self._dict.__delitem__(key)

    def __iter__(self):
        return self._dict.__iter__()

    def __str__(self):
        return "".join((self.__class__.__name__, "(", str(self._dict), ")"))


class SDMXSources(Catalog):
    """
     catalog of SDMX data sources, a.k.a. agencies 
    supported by pandaSDMX
    """

    name = "sdmx_sources"
    description = "SDMX sources supported by pandaSDMX"
    metadata = None
    ttl = 999999
    getenv = False
    getshell = False
    persist_mode = "default"
    version = __version__
    container = "catalog"
    partition_access = False

    def __init__(self, *args, **kwargs):
        super(SDMXSources, self).__init__(*args, **kwargs)
        # populate this catalog with empty sub-catalogs for each source.
        # This does not require remote access.
        # Sub-catalogs can read  the dataflows provided by each source.
        # exclude sources which do not support dataflows
        # and datasets (eg json-based ABS and OECD)
        excluded = ["ABS", "OECD", "IMF", "SGR", "STAT_EE"]
        for source_id, source in sdmx.source.sources.items():
            if source_id not in excluded:
                descr = source.name
                metadata = {"source_id": source_id}
                e = LocalCatalogEntry(
                    source_id,
                    descr,
                    SDMXDataflows,
                    direct_access=True,
                    args={},
                    cache=[],
                    parameters=[],
                    metadata=metadata,
                    catalog_dir="",
                    getenv=False,
                    getshell=False,
                    catalog=self,
                )
                self._entries[source_id] = e


class SDMXCodeParam(UserParameter):
    def __init__(self, allowed=None, **kwargs):
        super(SDMXCodeParam, self).__init__(**kwargs)
        self.allowed = allowed
        # isolate  codes from rich descriptions   
        # and store them as set for efficient validation
        self.allowed_codes = {c.partition(':')[0] for c in allowed}


    def validate(self, value):
        # Convert short-form multiple selections to list, e.g. 'DE+FR'
        if isinstance(value, str) and "+" in value:
            value = value.split("+")
        # Single code as str
        if isinstance(value, str):
            if value not in self.allowed_codes:
                raise ValueError(
                    "%s=%s is not one of the allowed values: %s"
                    % (self.name, value, ",".join(map(str, self.allowed_codes)))
                )
        # So value must be an  iterable  of str, e.g. multiple selection
        elif not all(c in self.allowed_codes for c in value):
            not_allowed = [c for c in value if c not in self.allowed_codes]
            raise ValueError(
                "%s=%s is not one of the allowed values: %s"
                % (self.name, not_allowed, ",".join(map(str, self.allowed_codes)))
            )
        return value


class SDMXDataflows(Catalog):
    """
     catalog of dataflows for a given SDMX source
    """

    version = __version__
    container = "catalog"
    partition_access = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entries = LazyDict(self._make_dataflow_entry)

        # read metadata on dataflows
        self.name = self.metadata["source_id"] + "_SDMX_dataflows"
        # Request dataflows from remote SDMX service
        self.req = sdmx.Request(self.metadata["source_id"])
        # get full list of dataflows
        self._flows_msg = self.req.dataflow()
        for flow_id in self._flows_msg.dataflow:
            self._entries[flow_id] = None

    def _make_dataflow_entry(self, flow_id):
        # Download metadata on specified dataflow
        flow_msg = self.req.dataflow(flow_id)
        flow = flow_msg.dataflow[flow_id]
        dsd = flow.structure
        descr = str(flow.name)
        metadata = self.metadata.copy()
        metadata["dataflow_id"] = flow_id
        metadata["structure_id"] = dsd.id
        # Make user params for coded dimensions
        # Check for any content constraints to codelists
        if hasattr(flow_msg, "constraint") and flow_msg.constraint:
            constraint = (
                next(iter(flow_msg.constraint.values())).data_content_region[0].member
            )
        else:
            constraint = None
        params = []
        # params for coded dimensions
        for dim in dsd.dimensions:
            lr = dim.local_representation
            # only dimensions with enumeration, i.e. where values are codes
            if lr.enumerated:
                ci = dim.concept_identity
                # Get code ID and  name as its description
                if constraint and dim.id in constraint:
                    codes_iter = (c for c in lr.enumerated.items.values()
                        if c in constraint[dim.id])
                else:
                    codes_iter =  lr.enumerated.items.values()
                codes = [':'.join((c.id, str(c.name)))
                    for c in codes_iter]
                
                # allow "" to indicate wild-carded dimension
                codes.append(":not specified")
                p = SDMXCodeParam(
                    name=dim.id,
                    description=str(ci.name),
                    type="str",
                    allowed=codes,
                    # set  default to "", ie. wild-card dimension
                    default="",
                )
                params.append(p)
        #  params for startPeriod and endPeriod
        year = date.today().year
        params.extend(
            [
                UserParameter(
                    name="startPeriod",
                    description="startPeriod",
                    type="datetime",
                    default=str(year - 1)
                ),
                UserParameter(
                    name="endPeriod",
                    description="endPeriod",
                    type="datetime"),
                UserParameter(
                    name='dtype',
                    description="""data type for pandas.DataFrame. See pandas docs 
                        for      allowed values. 
                        Default is '' which translates to 'float64'.""",
                    type='str'),
                UserParameter(
                    name='attributes',
                    description="""Include any attributes alongside observations in the DataFrame. See pandasdmx docx for details.
Examples: 'osgd' for all attributes, or 
'os': only attributes at observation and series level.""",
                    type='str'),
                UserParameter(
                    name='datetime',
                    description="""See pandasdmx docx for details.""",
                    type='bool',
                    default=True),
                UserParameter(
                    name='periods',
                    description="""Use 'FREQ' dimension to generate a PeriodIndex.""",
                    type='bool',
                    default=False),

                    ]
        )
        args = {p.name: f"{{{{{p.name}}}}}" for p in params}
        return LocalCatalogEntry(
            name=flow_id,
            description=descr,
            driver=SDMXData,
            direct_access=True,
            cache=[],
            parameters=params,
            args=args,
            metadata=metadata,
            catalog_dir="",
            getenv=False,
            getshell=False,
            catalog=self,
        )


class SDMXData(intake.source.base.DataSource):
    """
    Driver for SDMX data sets of  a given SDMX dataflow
    """

    version = __version__
    name = "sdmx_dataset"
    container = "dataframe"
    partition_access = True

    def __init__(self, metadata=None, **kwargs):
        super(SDMXData, self).__init__(metadata=metadata)
        self.name = self.metadata["dataflow_id"]
        self.req = sdmx.Request(self.metadata["source_id"])
        self.kwargs = kwargs

    def read(self):
        # construct key 
        key_ids = (p.name for p in self.entry._user_parameters 
            if isinstance(p, SDMXCodeParam))
        key = {i: self.kwargs[i] for i in key_ids 
            if self.kwargs[i]}
        # params for request. Currently, only start- and endPeriod are supported
        params = {k: str(self.kwargs[k].year)
            for k in ['startPeriod', 'endPeriod']}
        # remove endPeriod if it is prior to startPeriod (which is the default)
        if params['endPeriod'] < params['startPeriod']:
            del params['endPeriod']
        # Now request the data via HTTP
        # TODO: handle writer options and other Request.get kwargs eg. fromfile, timeout.
        data_msg = self.req.data(
            self.metadata['dataflow_id'], 
            key=key, 
            params=params)
        # get writer config. 
        # Capture only non-empty values as these will be filled by the writer
        writer_config = {k: self.kwargs[k]
            for k in ['dtype', 'attributes', 'datetime']
            if self.kwargs[k]}
        # massage some values  arg to conform to writer API
        periods = self.kwargs['periods']
        if periods: 
            writer_config['datetime'] = {'freq': 'FREQ'}
        self._dataframe = data_msg.to_pandas(**writer_config)
        return self._dataframe
        
            

    def _close(self):
        self._dataframe = None
