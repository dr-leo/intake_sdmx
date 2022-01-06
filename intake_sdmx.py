"""intake plugin for SDMX data sources"""


import intake
from intake.catalog import Catalog
from intake.catalog.utils import reload_on_change
from intake.catalog.local import LocalCatalogEntry, UserParameter
import pandasdmx as sdmx
from collections.abc import MutableMapping, MutableSequence
from datetime import date
from itertools import chain

__version__ = "0.1.0"


NOT_SPECIFIED = "n/a"
  
class LazyDict(MutableMapping):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._dict = dict(*args, **kwargs)
        self._func = func

    def update(self, *args, **kwargs):
        return self._dict.update(*args, **kwargs)

    def __getitem__(self, key):
        if self._dict[key] is None:
            self._dict[key] = self._func(key)
        return self._dict[key]

    def __setitem__(self, key, value):
        return self._dict.__setitem__(key, value)

    def __contains__(self, key):
        return self._dict.__contains__(key)

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

    name = "sdmx"
    description = "SDMX sources supported by pandaSDMX"
    version = __version__
    container = "catalog"

    def _load(self):
        # exclude sources which do not support dataflows
        # and datasets (eg json-based ABS and OECD)
        excluded = ["ABS", "OECD", "IMF", "SGR", "STAT_EE"]
        for source_id, source in sdmx.source.sources.items():
            if source_id not in excluded:
                descr = source.name
                metadata = {"source_id": source_id}
                e = LocalCatalogEntry(
                    source_id + "_SDMX_dataflows",
                    descr,
                    SDMXDataflows,
                    direct_access=True,
                    # set storage_options to {} if not set. This avoids TypeError
                    # when passing it to sdmx.Request() later
                    args={"storage_options": self.storage_options or {}},
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
    pass
    
    
class SDMXDataflows(Catalog):
    """
     catalog of dataflows for a given SDMX source
    """

    version = __version__
    container = "catalog"
    partition_access = False

    def _make_entries_container(self):
        return LazyDict(self._make_dataflow_entry)

    def _load(self):
        # read metadata on dataflows
        self.name = self.metadata["source_id"] + "_SDMX_dataflows"
        # Request dataflows from remote SDMX service
        self.req = sdmx.Request(self.metadata["source_id"], **self.storage_options)
        # get full list of dataflows
        self._flows_msg = self.req.dataflow()
        # to mapping from names to IDs for later back-translation
        # We use this catalog to store 2 entries per dataflow: ID and# human-readable name
        self.name2id = {}
        for dataflow in self._flows_msg.dataflow.values():
            flow_id, flow_name = dataflow.id, str(dataflow.name)
            # make 2 entries per dataflow using its ID and name
            self._entries[flow_id] = None
            self._entries[flow_name] = None
            self.name2id[flow_name] = flow_id

    def _make_dataflow_entry(self, flow_id):
        # if flow_id is actually its name, get the real id
        if flow_id in self.name2id:
            flow_id = self.name2id[flow_id]
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
                    codes_iter = (
                        c
                        for c in lr.enumerated.items.values()
                        if c in constraint[dim.id]
                    )
                else:
                    codes_iter = lr.enumerated.items.values()
                codes = list(chain(*((c.id, str(c.name)) for c in codes_iter)))

                # allow "" to indicate wild-carded dimension
                codes.append("")
                p = SDMXCodeParam(
                    name=dim.id,
                    description=str(ci.name),
                    type="mlist",
                    allowed=codes,
                    default=codes[:1],
                )
                params.append(p)
        # Try to retrieve ID of time and freq dimensions for DataFrame index
        dim_candidates = [d.id for d in dsd.dimensions if "TIME" in d.id]
        try:
            time_dim_id = dim_candidates[0]
        except IndexError:
            time_dim_id = NOT_SPECIFIED
        # Frequency for period index generation
        dim_candidates = [p.name for p in params if "FREQ" in p.name]
        try:
            freq_dim_id = dim_candidates[0]
        except IndexError:
            freq_dim_id = NOT_SPECIFIED
        # params for startPeriod and endPeriod
        year = date.today().year
        params.extend(
            [
                UserParameter(
                    name="startPeriod",
                    description="startPeriod",
                    type="str",
                    default=str(year - 1),
                ),
                UserParameter(
                    name="endPeriod", description="endPeriod", type="str"
                ),
                UserParameter(
                    name="dtype",
                    description="""data type for pandas.DataFrame. See pandas docs 
                        for      allowed values. 
                        Default is '' which translates to 'float64'.""",
                    type="str",
                ),
                UserParameter(
                    name="attributes",
                    description="""Include any attributes alongside observations 
                    in the DataFrame. See pandasdmx docx for details.
                    Examples: 'osgd' for all attributes, or 
                    'os': only attributes at observation and series level.""",
                    type="str",
                ),
                UserParameter(
                    name="index_type",
                    description="""Type of pandas Series/DataFrame index""",
                    type="str",
                    allowed=["object", "datetime", "period"],
                    default="object",
                ),
                UserParameter(
                    name="freq_dim",
                    description="""To generate PeriodIndex (index_type='period') 
                    Default is set based on heuristics.""",
                    type="str",
                    default=freq_dim_id,
                ),
                UserParameter(
                    name="time_dim",
                    description="""To generate datetime or period index. 
                        Ignored if index_type='object'.""",
                    type="str",
                    default=time_dim_id,
                ),
            ]
        )
        args = {p.name: f"{{{{{p.name}}}}}" for p in params}
        args["storage_options"] = self.storage_options
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

    @reload_on_change
    def search(self, text):
        words = text.lower().split()
        cat = SDMXDataflows(
            name=self.name + "_search",
            description=self.description,
            ttl=self.ttl,
            getenv=self.getenv,
            getshell=self.getshell,
            metadata=(self.metadata or {}).copy(),
            storage_options=self.storage_options,
        )
        cat.metadata["search"] = {"text": text, "upstream": self.name}
        cat.cat = self
        cat._entries._dict.clear()
        keys = [
            *chain.from_iterable(
                (self.name2id[k], k)
                for k in self
                if any(word in k.lower() for word in words)
            )
        ]
        cat._entries.clear()
        cat._entries.update({k: None for k in keys})
        return cat

    def filter(self, func):
        raise NotImplemented


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
        self.req = sdmx.Request(self.metadata["source_id"], **self.storage_options)
        self.kwargs = kwargs

    def read(self):
        # construct key
        key_ids = (
            p.name for p in self.entry._user_parameters if isinstance(p, SDMXCodeParam)
        )
        key = {i: self.kwargs[i] for i in key_ids if self.kwargs[i]}
        # params for request. Currently, only start- and endPeriod are supported
        params = {k: self.kwargs[k] for k in ["startPeriod", "endPeriod"]}
        # remove endPeriod if it is prior to startPeriod (which is the default)
        if params["endPeriod"] < params["startPeriod"]:
            del params["endPeriod"]
        # Now request the data via HTTP
        # TODO: handle   Request.get kwargs eg. fromfile, timeout.
        data_msg = self.req.data(self.metadata["dataflow_id"], key=key, params=params)
        # get writer config.
        # Capture only non-empty values as these will be filled by the writer
        writer_config = {
            k: self.kwargs[k] for k in ["dtype", "attributes"] if self.kwargs[k]
        }
        # construct  args   to conform to writer API
        index_type = self.kwargs["index_type"]
        freq_dim = self.kwargs["freq_dim"]
        time_dim = self.kwargs["time_dim"]
        if index_type == "datetime":
            writer_config["datetime"] = True if freq_dim == NOT_SPECIFIED else freq_dim
        elif index_type == "period":
            datetime = {}
            datetime["freq"] = True if freq_dim == NOT_SPECIFIED else freq_dim
            datetime["dim"] = True if time_dim == NOT_SPECIFIED else time_dim
            writer_config["datetime"] = datetime
        # generate the Series or dataframe
        self._dataframe = data_msg.to_pandas(**writer_config)
        return self._dataframe

    def _close(self):
        self._dataframe = None
