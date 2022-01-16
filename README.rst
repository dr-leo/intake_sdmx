intake_sdmx: an intake plugin for SDMX data sources
======================================================

(c) 2021 Dr. Leo

`Source code @ Github <https://github.com/dr-leo/intake_sdmx/>`_ —

**intake_sdmx** is an `Apache 2.0-licensed <LICENSE>`_ 
`intake <http://intake.readthedocs.io>`_ plugin for SDMX-compliant data sources
such as BIS, ECB, ESTAT, INSEE, ILO, UN, UNICEF, World Bank and more. 
**intake_sdmx** leverages `pandaSDMX <http://pandasdmx.readthedocs.io>`_.

Quick start
=============

* install intake_sdmx and dependencies with `conda install intake_sdmx -c intake` 


Features:
=========================

* catalog of SDMX data sources  populated 
  from data sources supported by pandaSDMX
* each entry is a sub-catalog of dataflows provided by that data source. This works only
  for SDMXML-based data sources, but not for JSON-based ones (OECD, ABS etc.).
* Dataflow entries are stored in a subcatalog
  as a lazy dict, i.e. the actual
  metadata (= DataStructureDefinition, code lists etc.) are 
  downloaded only when
  instantiating a  particular Dataflow.
  Each dataflow occurs twice in the list: first under its dataflow_id (eg. 'EXR'),
  second, under its human-readable description (eg. 'Exchange Rates'). However, accessing
  a dataflow by its description, will return the same
  instance as when accessed by ID.  
* Dataflows catalog has a search method which returns
  a catalog of entries where at least one of the wordsoccur in the dataflow's human-readable
  description. 
* pass kwargs to a data source to specify a 
  key (= dimension values), startPeriod and endPeriod. The key is validated against the code lists for each coded dimension. This facilitates cube selection for querying  actual datasets. 
* download a dataset and return a pandas Series or dataframe
  kwargs to configure the export process can be specified. Doing so,
  a dataframe with datetime index, period index, or a Series withmulti-level index can be generated.
  
  
License
-------

Copyright 2021, Dr. Leo

Licensed under the Apache License, Version 2.0 (the “License”); you may not use
these files except in compliance with the License. You may obtain a copy of the
License:

- from the file LICENSE included with the source code, or
- at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

