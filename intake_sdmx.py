"""intake plugin for SDMX data sources"""



import intake
from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry
import pandasdmx as sdmx

__version__ = '0.0.1'



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
        self.read()

    def read(self):
        for source_id, source in sdmx.source.sources.items():
            descr = source.name
            metadata = {'source_id' : source_id}
            e = LocalCatalogEntry(source_id, descr, SDMXDataflows, direct_access=True, 
                args={},
                 cache=[], parameters=[], metadata=metadata, catalog_dir='',
                 getenv=False, getshell=False, catalog=self)
            self._entries[source_id] = e


class SDMXDataflows(Catalog):
    '''
     catalog of dataflows for a given SDMX source
    '''
    version = __version__
    container = 'catalog'
    partition_access = False
    
    def read(self):
        self.name = self.metadata['source_id'] + '_SDMX_dataflows'
        # Request dataflows from remote SDMX service
        req = sdmx.Request(self.metadata['source_id'])
        flows_msg = req.dataflow()
        for flow_id, flow in flows_msg.dataflow.items():
            descr = flow.name.en
            metadata = self.metadata.copy()
            metadata['dataflow_id'] = flow_id
            e = LocalCatalogEntry(flow_id, descr, SDMXData, direct_access=True, args={},
                 cache=[], parameters=[], metadata=metadata, catalog_dir='',
                 getenv=False, getshell=False, catalog=self)
            self._entries[flow_id] = e

class SDMXData(intake.source.base.DataSource):
    '''
    Driver for SDMX data sets of  a given SDMX dataflow
    '''
    version = __version__
    name = 'sdmx_dataset'
    container = 'dataframe'
    partition_access = True

    def __init__(self,  metadata={}):
        super(SDMXData, self).__init__( metadata=metadata)
        name = metadata['dataflow_id']
        self.name = name
        
    
    def read(self):
        name = self.metadata['dataflow_id'] + '_resources'
    

    def _get_schema(self):
        # Request structural metadata from the source.
        req = sdmx.Request(self.metadata['source_id'])
        flow_id = self.metadata['dataflow_id']
        flow_msg = req.dataflow(flow_id)
        # Get dimensions from the datastructure-definition
        # and gather allowed values from  
        # the  codelists.
        # TODO: honor any content constraints
        dsd = flow_msg.dataflow[flow_id].structure
        dim_l = list(dsd.dimensions)
        user_params = []
        for d in dim_l:
            cl = d.local_representation.enumerated 
            if cl:
                try:
                    descr = cl.description.en
                except AttributeError:
                    descr = None
                param = {
                    'name': d.id,
                    'description': descr,
                    'type': 'list[str]'
                }
                if d in allowed_values:
                    v = allowed_values[d].aslist()
                else:
                    # take codes from the codelists
                    v = list(cl.keys())
                param['allowed'] = v
                user_parameters.append(param)
                
                # TODO: startPeriod, endPeriod

    def read(self):
        return # pd dataframe from pandasdmx
    
    def _close(self):
        self._dataframe = None
    
