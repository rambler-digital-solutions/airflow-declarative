..
.. Copyright 2017, Rambler Digital Solutions
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

===================
airflow-declarative
===================

Airflow declarative DAGs via YAML.

Compatibility:

- Python 2.7 / 3.5+
- Airflow 1.10.4+

Key Features
============

- Declarative DAGs in plain text YAML helps a lot to understand how DAG will
  looks like. Made for humans, not programmers.
- It makes extremely hard to turn your DAGs into code mess. Even if you make
  complicated YAMLs generator the result would be readable for humans.
- No more guilty about coupling business logic with task management system
  (Airflow). They now could coexists separated.
- Static analysis becomes a trivial task.
- It's a good abstraction to create your own scheduler/worker compatible with
  original Airflow one.

Examples
========

Check `tests/dags` directory for example of DAGs which will works and which
won't. Use `src/airflow_declarative/schema.py` module for the reference about
YAML file schema. It should be self descriptive.

Don't be shy to experiment: `trafaret-config`_ will help you to understand
what had gone wrong and why and where.

.. _trafaret-config: https://pypi.python.org/pypi/trafaret-config

Usage
=====

We provide support for two installation options:

1. As a complementary side package for the upstream Airflow.
2. As a built-in Airflow functionality using patches for Airflow.

Upstream Airflow
----------------

The idea is to put a Python script to the ``dags_folder`` which would
load the declarative dags via airflow_declarative. More details:
`Installation using Upstream Airflow`_.

.. code-block:: python

    import os

    import airflow_declarative

    # Assuming that the yaml dags are located in the same directory
    # as this Python module:
    root = os.path.dirname(__file__)

    dags_list = [
        airflow_declarative.from_path(os.path.join(root, item))
        for item in os.listdir(root)
        if item.endswith((".yml", ".yaml"))
    ]

    globals().update({dag.dag_id: dag for dags in dags_list for dag in dags})


Patched Airflow
---------------

We provide ready to use patches in the `patches`_ directory. To use them
you will need to apply a patch to a corresponding Airflow version and then
build it yourself. More details: `Installation using Patched Airflow`_.

.. _Installation using Upstream Airflow: https://airflow-declarative.readthedocs.io/en/latest/installation.html#upstream-airflow
.. _Installation using Patched Airflow: https://airflow-declarative.readthedocs.io/en/latest/installation.html#patched-airflow
.. _patches: https://github.com/rambler-digital-solutions/airflow-declarative/blob/master/patches
