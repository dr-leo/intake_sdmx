intake_sdmx: an intake plugin for SDMX data sources
======================================================

`Source code @ Github <https://github.com/dr-leo/intake_sdmx/>`_ —
`Authors <AUTHORS>`_

**intake_sdmx** is an `Apache 2.0-licensed <LICENSE>`_ 
`intake <http://intake.readthedocs.io>`_ plugin for SDMX-compliant data sources
such as BIS, ECB, ESTAT, INSEE, ILO, UNDS, UNICEF and more. 
**intake_sdmx** leverages `pandaSDMX <http://pandasdmx.readthedocs.io>`_.

Quick start
=============

* install intake with `pip install intake` or `conda install intake`.
* Clone this repo and install intake_sdmx from the package root with pip.
* from the package root, run `pytest`.

Development status
===================

As of April 2021, intake_sdmx is merely a proof of concept. It lacks key features such asdownloading datasets. 

Implemented features:
=================

* catalog of SDMX data sources opened and populated correctly
  from data sources supported by pandaSDMX
* each entry is a sub-catalog of dataflows provided by that data source. This works only
  for SDMXML-based data sources, but not for JSON-based ones (OECD, ABS etc.).
* read() method downloads the dataflows and stores them as entries. Those are
  not very useful, yet. They contain some metadata such as the dataflow_id anddescription,   
  but access to datasets is not yet implemented.
  
  
License
-------

Copyright 2014–2021, `pandaSDMX developers <AUTHORS>`_

Licensed under the Apache License, Version 2.0 (the “License”); you may not use
these files except in compliance with the License. You may obtain a copy of the
License:

- from the file LICENSE included with the source code, or
- at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

