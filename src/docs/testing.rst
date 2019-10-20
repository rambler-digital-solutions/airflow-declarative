Testing Declarative DAGs
========================

Unlike DAGs defined with Python, declarative DAGs forcibly draw a strong line
between the business logic (the Python callbacks and external commands)
and the DAG definition. This obligatory separation brings some benefits:

- The business logic doesn't have to know anything about Airflow existence
  (except the :ref:`task context dict <operator_sensor>`).
- The declaratively defined DAG doesn't have to be executed by Airflow.
  A custom implementation could be created which could execute the DAGs
  described with YAML, which is easy to parse.
- It is much clearer what has to be tested and what is not.

The business logic is completely under your responsibility so it should
be covered with tests.

The DAG instantiation, however, is not your responsibility, so it
doesn't have to be covered with tests. It is just enough to ensure
that the declarative DAG passes the schema validation and looks sensible
(i.e. all required operators and sensors are defined, the :ref:`flow <flow>`
contains all required links).

The schema validation could be automated with the following test:

::

    from pathlib import Path

    import airflow_declarative
    import pytest
    from airflow import DAG


    DAG_DIR = Path("share") / "airflow"


    @pytest.mark.parametrize("dag_path", DAG_DIR.glob("*.yaml"))
    def test_load_airflow_dags(dag_path):
        dags = airflow_declarative.from_path(dag_path)
        assert all(isinstance(dag, DAG) for dag in dags)

This test assumes that all of your declarative DAGs are located in
the ``share/airflow`` directory. It loads all yamls from that directory,
validates their schemas and transforms them to :class:`airflow.models.DAG`
instances. If a declarative DAG passes this test, then it can be loaded
by the actual Airflow.
