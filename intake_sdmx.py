
import intake
from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry
import pandasdmx as sdmx

__version__ = '0.0.1'



class SourcesDriver(intake.source.base.DataSource):
    '''
    Driver returning a catalog of SDMX data sources, a.k.a. agencies 
    supported by pandaSDMX
    '''
    name = 'sdmx_sources_driver'
    version = __version__
    container = 'catalog'
    partition_access = False
    
    def read(self):
        return SourceCatalog(name='sdmx_sources', 
            description='SDMX sources supported by pandaSDMX', 
            metadata=None, ttl=999999, 
            getenv=False, getshell=False, 
            persist_mode='default', storage_options=None)
    

class SourcesCatalog(Catalog):
    def _load(self):
        for source_id, source in sdmx.source.sources.items():
            descr = source.name
            metadata = {'source_id' : source_id}
            e = LocalCatalogEntry(source_id, descr, Dataflows, direct_access=True, 
                args={},
                 cache=[], parameters=[], metadata=metadata, catalog_dir='',
                 getenv=False, getshell=False, catalog=self)
            self._entries[source_id] = e

class Dataflows(intake.source.base.DataSource):
    '''
    Driver returning a catalog of dataflows for a given SDMX source
    '''
    version = __version__
    name = 'sdmx_dataflows'
    container = 'catalog'
    partition_access = False

    def __init__(self, metadata={}):
        super(SDMXDataflows, self).__init__(metadata=metadata)
    
    def read(self):
        name = self.metadata['source_id'] + '_SDMX_dataflows'
        return SDMXDataflowsCat(name=name, metadata=self.metadata)
    
    
class DataflowsCatalog(Catalog):

    def _load(self):
        # Request dataflows from remote SDMX service
        req = sdmx.Request(self.metadata['source_id'])
        flows_msg = req.dataflow()
        for flow_id, flow in flows_msg.dataflow.items():
            descr = flow.name.en
            metadata = self.metadata.copy()
            metadata['dataflow_id'] = flow_id
            e = LocalCatalogEntry(flow_id, descr, DataSet, direct_access=True, args={},
                 cache=[], parameters=[], metadata=metadata, catalog_dir='',
                 getenv=False, getshell=False, catalog=self)
            self._entries[flow_id] = e

class DataSet(intake.source.base.DataSource):
    '''
    Driver returning a data set for a given SDMX dataflow
    '''
    version = __version__
    name = 'sdmx_dataset'
    container = 'dataframe'
    partition_access = False

    def __init__(self, metadata={}):
        super(SDMXDataflowResources, self).__init__(metadata=metadata)
    
    def read(self):
        name = self.metadata['dataflow_id'] + '_resources'
        return SDMXResourcesCat(name=name, metadata=self.metadata)
    


class SDMXData(intake.source.base.DataSource):
    '''
    intake driver for SDMX datasets.
    '''
    name = 'sdmx_data'
    version = __version__
    container = 'dataframe'
    partition_access = False

    def __init__(self, metadata=None):
        self._dataframe = None
        super(SDMXData, self).__init__(metadata=metadata)


    def _get_schema(self):
        # Request structural metadata from the source.
        req = sdmx.Request(metadata['source_id'])
        flow_id = self.metadata['dataflow_id']
        flow_msg = req.dataflow(flow_id)
        # check for  constraints
        try:
            cr = list(flow_msg.constraint.values())[0].data_content_region[0]
            allowed_values = sdmx.to_pandas(cr)
        except Exception:
            allowed_values = {}
        # Get dimensions from the datastructure-definition
        # and gather values either from the constraint or
        # the unconstrained codelists
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
    
