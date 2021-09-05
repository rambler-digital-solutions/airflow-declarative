try:
    # Python 3
    from collections.abc import Iterable, Mapping
except ImportError:  # pragma: no cover
    # Python 2.7
    from collections import Iterable, Mapping


try:
    # Airflow 2
    from airflow.sensors.base import BaseSensorOperator
except ImportError:  # pragma: no cover
    try:
        # Since Airflow 1.10
        from airflow.sensors.base_sensor_operator import BaseSensorOperator
    except ImportError:
        from airflow.operators.sensors import BaseSensorOperator


try:
    # Airflow 2
    from airflow.models import BaseOperator
except ImportError:  # pragma: no cover
    from airflow.operators import BaseOperator

try:
    # Airflow 2
    from airflow.utils.dag_cycle_tester import test_cycle as _test_cycle
except ImportError:  # pragma: no cover
    _test_cycle = None


__all__ = ("BaseOperator", "BaseSensorOperator", "Iterable", "Mapping", "test_cycle")


def test_cycle(dag):
    if _test_cycle is not None:
        # Airflow 2
        _test_cycle(dag)
    elif hasattr(dag, "test_cycle"):
        # Since Airflow 1.10
        dag.test_cycle()
