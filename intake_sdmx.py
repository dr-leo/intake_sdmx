"""intake plugin for SDMX data sources"""



import intake
from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry, UserParameter
import pandasdmx as sdmx
from collections.abc import MutableMapping

__version__ = '0.0.2'


class LazyDict(MutableMapping):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._dict = dict(*args, **kwargs)
        self._func = func
        
    def __getitem__(self, key):
        if self._dict[key] is  None:
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
        return ''.join((self.__class__.__name__, '(', str(self._dict), ')'))
    
    
class SDMXSources(Catalog):
    '''
     catalog of SDMX data sources, a.k.a. agencies 
    supported by pandaSDMX
    '''
    name = 'sdmx_sources'
    description='SDMX sources supported by pandaSDMX' 
    metadata=None
    ttl=999999 
    getenv=False 
    getshell=False 
    persist_mode='default' 
    version = __version__
    container = 'catalog'
    partition_access = False
    
    def __init__(self, *args, **kwargs):
        super(SDMXSources, self).__init__(*args, **kwargs)
        # populate this catalog with empty sub-catalogs for each source. 
        # This does not require remote access. 
        # Sub-catalogs can read  the dataflows provided by each source.
        # exclude sources which do not support dataflows 
        # and datasets (eg json-based ABS and OECD)
        excluded = ['ABS', 'OECD', 'IMF', 'SGR', 'STAT_EE']         
        for source_id, source in sdmx.source.sources.items():
            if source_id not in excluded:
                descr = source.name
                metadata = {'source_id' : source_id}
                e = LocalCatalogEntry(source_id, descr, SDMXDataflows, direct_access=True, 
                    args={},
                     cache=[], parameters=[], metadata=metadata, catalog_dir='',
                     getenv=False, getshell=False, catalog=self)
                self._entries[source_id] = e

class SDMXCodeParam(UserParameter):
    def validate(self, value):
        # Convert short-form multiple selections to list, e.g. 'DE+FR'
        if isinstance(value, str) and '+' in value:
            value = value.split('+')
        # Make allowed codes as list, 
        # i.e. extract the key from each dict
        allowed_codes = [next(iter(c)) for c in self.allowed]        
        # Single code as str
        if isinstance(value, str): 
            if (value not in allowed_codes):
                raise ValueError('%s=%s is not one of the allowed values: %s' % (
                    self.name, value, ','.join(map(str, self.allowed))))
        # So value must be an  iterable  of str, e.g. multiple selection
        elif not all(c in allowed_codes for c in value): 
            not_allowed = [c for c in value if c not in  allowed_codes]
            raise ValueError('%s=%s is not one of the allowed values: %s' % (
            self.name, not_allowed, ','.join(map(str, self.allowed))))
        return value

class SDMXDataflows(Catalog):
    '''
     catalog of dataflows for a given SDMX source
    '''
    version = __version__
    container = 'catalog'
    partition_access = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entries = LazyDict(self._make_dataflow_entry)
        
        # read metadata on dataflows
        self.name = self.metadata['source_id'] + '_SDMX_dataflows'
        # Request dataflows from remote SDMX service
        self.req = sdmx.Request(self.metadata['source_id'])
        # get full list of dataflows
        self._flows_msg = self.req.dataflow()
        for  flow_id in self._flows_msg.dataflow:
            self._entries[flow_id] = None  

    def _make_dataflow_entry(self, flow_id):
        # Download metadata on specified dataflow
        flow_msg = self.req.dataflow(flow_id)
        flow = flow_msg.dataflow[flow_id]
        dsd = flow.structure
        descr = flow.name.en
        metadata = self.metadata.copy()
        metadata['dataflow_id'] = flow_id
        metadata['structure_id'] = dsd.id
        # Make user params for coded dimensions
        # Check for any content constraints to codelists
        if hasattr(flow_msg, 'constraint'):
            constraint = next(iter(flow_msg.constraint.
                values())).data_content_region[0].member
        else:
            constraint = None
        params = []
        # params for coded dimensions
        for dim in dsd.dimensions:
            lr = dim.local_representation
            # only dimensions with enumeration, i.e. where values are codes
            if lr.enumerated:
                ci = dim.concept_identity
                # Get code ID and English name as its description
                if constraint and dim.id in constraint:
                    codes = [{c.id : c.name.en} for c in lr.enumerated.items.values() if c in constraint[dim.id]]
                else:
                    codes = [{c.id : c.name.en} for c in lr.enumerated.items.values()]
                p = SDMXCodeParam(
                    name=dim.id,
                    description=ci.name.en,
                    type=None,
                    allowed=codes,
# set first code as default                    
                    default=next(iter(codes[0])))
                params.append(p)
                
        return LocalCatalogEntry(name=flow_id, description=descr, driver=SDMXData, direct_access=True, 
             cache=[], parameters=params, 
             metadata=metadata, catalog_dir='',
             getenv=False, getshell=False, catalog=self)
                 

class SDMXData(intake.source.base.DataSource):
    '''
    Driver for SDMX data sets of  a given SDMX dataflow
    '''
    version = __version__
    name = 'sdmx_dataset'
    container = 'dataframe'
    partition_access = True

    def __init__(self, **kwargs):
        super(SDMXData, self).__init__(**kwargs)
        name = self.metadata['dataflow_id']
        self.name = name
        self.kwargs = kwargs
        
    
    def read(self):
        name = self.metadata['dataflow_id'] + '_resources'
    
    def _close(self):
        self._dataframe = None
    
