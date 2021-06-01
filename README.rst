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

* install intake with `pip install intake` or `conda install intake`.
* Clone this repo and install intake_sdmx from the package root with pip.
* from the package root, run `pytest`.

Development status
===================

As of June 2021, most intended core features have been implemented, if hardly tested.

Implemented features:
=================

* catalog of SDMX data sources opened and populated correctly
  from data sources supported by pandaSDMX
* each entry is a sub-catalog of dataflows provided by that data source. This works only
  for SDMXML-based data sources, but not for JSON-based ones (OECD, ABS etc.).
* Dataflow entries are stored in a subcatalog
  as a lazy dict, i.e. the actual
  metadata (= DataStructureDefinition, CodeLIsts etc.) are 
  downloaded only when
  instantiating a data source for a particular Dataflow. 
  Thus, even the human-readable description of a Dataflow is 
  visible only after creating the data source. 
  Thus, the list of dataflows cannot be searched by keywords. 
  This feature should be added asap.
* pass kwargs to a data source to specify a 
  key (= dimension values), startPeriod and endPeriod.
* download a dataset and return a pandas dataframe
  
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

