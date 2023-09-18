..
.. Copyright 2019, Rambler Digital Solutions
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
.. http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
..


Introduction
============

The primary way of constructing DAGs in Airflow is by describing them
in Python: `<https://airflow.apache.org/tutorial.html>`_.

`airflow_declarative` transforms the DAGs defined with YAML to their
Python equivalents.

The public API is pretty simple: there are just 2 functions, both
returning the :class:`airflow.models.dag.DAG` instances:

.. autofunction:: airflow_declarative.from_path

.. autofunction:: airflow_declarative.from_dict
