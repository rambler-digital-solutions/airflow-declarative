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

__all__ = ("BaseOperator", "BaseSensorOperator", "Iterable", "Mapping")
