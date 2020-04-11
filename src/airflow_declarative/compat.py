try:
    # Python 3
    from collections.abc import Iterable, Mapping
except ImportError:
    # Python 2.7
    from collections import Iterable, Mapping


try:
    # Since Airflow 1.10
    from airflow.sensors.base_sensor_operator import BaseSensorOperator
except ImportError:
    from airflow.operators.sensors import BaseSensorOperator


try:
    # Airflow master
    from airflow.models import BaseOperator
except ImportError:
    from airflow.operators import BaseOperator

try:
    # Airflow master
    from airflow.utils.dag_cycle_tester import test_cycle as _test_cycle
except ImportError:
    _test_cycle = None


__all__ = ("BaseOperator", "BaseSensorOperator", "Iterable", "Mapping", "test_cycle")


def test_cycle(dag):
    if _test_cycle is not None:
        # Airflow master
        _test_cycle(dag)
    elif hasattr(dag, "test_cycle"):
        # Since Airflow 1.10
        dag.test_cycle()
