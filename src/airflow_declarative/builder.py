# -*- coding: utf-8 -*-
#
# Copyright 2017, Rambler Digital Solutions
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import absolute_import, division, print_function, unicode_literals

from .compat import test_cycle
from .schema import ensure_schema


def build_dags(schema, dag_class=None, operator_class=None, sensor_class=None):
    """
    :param dict schema: Airflow declarative DAGs schema.
    :param dag_class: DAG class. When not specified, the ``airflow.models.DAG``
                                 get used via implicit import.
    :param type operator_class: Airflow operator class.
    :param type sensor_class: Airflow sensor class.
    :rtype: list[airflow.models.DAG]
    """
    schema = ensure_schema(schema)

    # We use implicit airflow imports by following reasons:
    # 1. Airflow project get renamed recently to apache-airflow, so we couldn't
    #    have (yet) stable dependency on it without conflicts.
    # 2. We put the first stone here provide support for custom scheduler and
    #    worker implementations.
    #
    if dag_class is None:  # pragma: no cover
        from airflow import DAG as dag_class
    if operator_class is None:  # pragma: no cover
        from .operators import GenericOperator as operator_class
    if sensor_class is None:  # pragma: no cover
        from .operators import GenericSensor as sensor_class

    return [
        build_dag(
            dag_id,
            dag_schema,
            dag_class=dag_class,
            operator_class=operator_class,
            sensor_class=sensor_class,
        )
        for dag_id, dag_schema in schema["dags"].items()
    ]


def build_dag(dag_id, schema, dag_class, operator_class, sensor_class):
    """
    :param str dag_id: DAG ID.
    :param dict schema: DAG definition schema.
    :param dag_class: DAG class.
    :param type operator_class: Airflow operator class.
    :param type sensor_class: Airflow sensor class.
    :rtype: airflow.models.DAG
    """
    dag = dag_class(dag_id=dag_id, **schema.get("args", {}))

    sensors = {
        sensor_id: build_sensor(
            dag, sensor_id, sensor_schema, sensor_class=sensor_class
        )
        for sensor_id, sensor_schema in schema.get("sensors", {}).items()
    }

    operators = {
        operator_id: build_operator(
            dag, operator_id, operator_schema, operator_class=operator_class
        )
        for operator_id, operator_schema in schema.get("operators", {}).items()
    }

    duplicates = set(sensors) & set(operators)
    if duplicates:
        raise RuntimeError(
            "Tasks: %s - are both sensors and operators" % ", ".join(duplicates)
        )

    build_flow(dict(operators, **sensors), schema.get("flow", {}))

    test_cycle(dag)

    return dag


def build_sensor(dag, sensor_id, sensor_schema, sensor_class):
    """
    :param DAG dag: Airflow DAG instance.
    :param str sensor_id: Sensor ID.
    :param dict sensor_schema: Sensor definition schema.
    :param type sensor_class: Airflow sensor class.
    :rtype: airflow.operators.sensors.BaseSensorOperator
    """
    return build_task(dag, sensor_id, sensor_schema, task_class=sensor_class)


def build_operator(dag, operator_id, operator_schema, operator_class):
    """
    :param DAG dag: Airflow DAG instance.
    :param str operator_id: Operator ID.
    :param dict operator_schema: Operator definition schema.
    :param type operator_class: Airflow operator class.
    :rtype: airflow.operators.BaseOperator
    """
    return build_task(dag, operator_id, operator_schema, task_class=operator_class)


def build_task(dag, task_id, schema, task_class):
    """
    :param airflow.models.DAG dag: DAG object instance.
    :param str task_id: Task ID.
    :param dict schema: Task schema.
    :param type task_class: Airflow operator class.
    :rtype: airflow.operators.BaseOperator
    """
    args = schema.get("args", {})

    callback = schema.get("callback", None)
    if callback is not None:
        callback_args = schema.get("callback_args", {})
        return task_class(
            _callback=callback,
            _callback_args=callback_args,
            task_id=task_id,
            dag=dag,
            **args
        )

    task_class = schema.get("class", None)  # type: type
    if task_class is not None:
        return task_class(task_id=task_id, dag=dag, **args)

    # Basically, you cannot reach here - schema validation should prevent this.
    # But in case if you're lucky here is your exception.
    raise RuntimeError(
        "nothing to do with %s: %s" % (task_id, schema)
    )  # pragma: no cover


def build_flow(tasks, schema):
    """
    :param dict tasks: Tasks mapping by their ID.
    :param dict schema: Flow schema.
    """
    for task_id, downstream_ids in schema.items():
        try:
            task = tasks[task_id]
        except KeyError:
            raise RuntimeError("unknown task `%s` in flow" % task_id)
        else:
            downstream_tasks = []
            for downstream_idx in downstream_ids:
                try:
                    downstream_tasks.append(tasks[downstream_idx])
                except KeyError:
                    raise RuntimeError(
                        "unknown downstream task `%s` for %s"
                        "" % (downstream_idx, task_id)
                    )
            task.set_downstream(downstream_tasks)
