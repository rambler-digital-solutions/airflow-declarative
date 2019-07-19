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

Installation
============

.. _upstream_airflow:

Option 1: Upstream Airflow
--------------------------

This is a simplest option which you would probably want to go with
if you're just evaluating Declarative.

The idea is simple:

1. Install `airflow_declarative` Python package (e.g. with
   ``pip install airflow_declarative``)
2. In the Airflow's ``dags_folder`` create a new Python module
   (e.g. ``declarative_dags.py``), which would expose the Declarative DAGs:

::

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


That's enough to get started.

None of the other Python DAGs would be affected
in any way, so you can start gradually migrating to Declarative DAGs.

However, this approach has some shortcomings:

1. If any of the Declarative yamls would fail to load, none of the Declarative
   DAGs would get loaded (because the Python module would raise
   an exception during the DAG import phase)
2. There's a ``dagbag_import_timeout`` configuration setting in Airflow,
   which sets a timeout in seconds for a single Python DAG module import.
   This timeout would apply to loading all Declarative DAGs at once,
   which might be an issue if there are long commands in the dynamic
   `do`/`with_items` blocks.
3. The ``Code`` tab of a DAG in the web interface would show the source
   of the Python shim module instead of the DAGs' yamls.


.. _patched_airflow:

Option 2: Patched Airflow
-------------------------

Airflow might be patched to have a built-in support for Declarative DAGs,
which doesn't have the limitations listed above in the first option.

In this case, the Python shim is not needed. Airflow would natively load
the yaml DAGs as if they were in Python.

We provide ready to use patches in the `patches`_ directory, which
are named after an Airflow release that they were made for. Only one
patch should be applied (the one that matches your Airflow version).

.. _patches: https://github.com/rambler-digital-solutions/airflow-declarative/blob/master/patches

To apply a patch, you would need to build your own distribution of Airflow
instead of installing one from PyPI.

To achieve that, the following (roughly) should be done:

::

    AIRFLOW_VERSION=1.10.4
    AIRFLOW_DEPS=celery,postgres

    curl -o declarative.patch https://raw.githubusercontent.com/rambler-digital-solutions/airflow-declarative/master/patches/${AIRFLOW_VERSION}.patch
    pip download --no-binary=:all: --no-deps apache-airflow==${AIRFLOW_VERSION}
    tar xzf apache-airflow-*.tar.gz
    cd apache-airflow-*/
    patch -p1 < ../declarative.patch
    pip install ".[${AIRFLOW_DEPS}]"
