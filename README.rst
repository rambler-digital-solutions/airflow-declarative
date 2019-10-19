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
- Airflow 1.10+

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

Upstream Airflow
----------------

To use with current (up to 1.8.2 release) upstream Airflow, you need to provide
DAGs via Python file anyway. That should looks something like this:

.. code-block:: python

    import os

    import airflow_declarative

    # Assuming that the yaml dags are located in the same directory
    # as this Python dag module:
    ROOT = os.path.dirname(__file__)

    DAGS = [
        airflow_declarative.from_path(os.path.join(ROOT, item))
        for item in os.listdir(ROOT)
        if item.endswith((".yml", ".yaml"))
    ]

    globals().update({dag.dag_id: dag for dags in DAGS for dag in dags})

And place such file to ``AIRFLOW_HOME`` directory. Airflow will load dags in
old fashion way.

Patched Airflow
---------------

Checkout `patches` directory for patches against Airflow release to have native
declarative dags support on it. In this case no Python files are need on
``AIRFLOW_HOME`` path - just put there your YAMLs, they'll get loaded
automagically.
