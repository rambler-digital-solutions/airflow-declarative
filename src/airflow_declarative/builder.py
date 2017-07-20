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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from .schema import ensure_schema


def build_dags(schema, dag_class=None):
    """
    :param dict schema: Airflow declarative DAGs schema.
    :param dag_class: DAG class. When not specified, the ``airflow.models.DAG``
                                 get used via implicit import.
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

    return [build_dag(dag_id, dag_schema,
                      dag_class=dag_class)
            for dag_id, dag_schema in schema['dags'].items()]


def build_dag(dag_id, schema, dag_class):
    """
    :param str dag_id: DAG ID.
    :param dict schema: DAG definition schema.
    :param dag_class: DAG class.
    :rtype: airflow.models.DAG
    """
    dag = dag_class(dag_id=dag_id, **schema.get('args', {}))

    sensors = {
        sensor_id: build_sensor(dag, sensor_id, sensor_schema)
        for sensor_id, sensor_schema in schema.get('sensors', {}).items()
    }

    operators = {
        operator_id: build_operator(dag, operator_id, operator_schema)
        for operator_id, operator_schema in schema.get('operators', {}).items()
    }

    duplicates = set(sensors) & set(operators)
    if duplicates:
        raise RuntimeError('Tasks: %s - are both sensors and operators'
                           '' % ', '.join(duplicates))

    build_flow(dict(operators, **sensors), schema.get('flow', {}))

    return dag


def build_sensor(dag, sensor_id, sensor_schema):
    """
    :param DAG dag: Airflow DAG instance.
    :param str sensor_id: Sensor ID.
    :param dict sensor_schema: Sensor definition schema.
    :rtype: airflow.operators.sensors.BaseSensorOperator
    """
    return build_task(dag, sensor_id, sensor_schema)


def build_operator(dag, operator_id, operator_schema):
    """
    :param DAG dag: Airflow DAG instance.
    :param str operator_id: Operator ID.
    :param dict operator_schema: Operator definition schema.
    :rtype: airflow.operators.BaseOperator
    """
    return build_task(dag, operator_id, operator_schema)


def build_task(dag, task_id, schema):
    """
    :param airflow.models.DAG dag: DAG object instance.
    :param str task_id: Task ID.
    :param dict schema: Task schema.
    :rtype: airflow.operators.BaseOperator
    """
    task_class = schema['class']
    args = schema.get('args', {})
    return task_class(task_id=task_id, dag=dag, **args)


def build_flow(tasks, schema):
    """
    :param dict tasks: Tasks mapping by their ID.
    :param dict schema: Flow schema.
    """
    for task_id, downstream_ids in schema.items():
        try:
            task = tasks[task_id]
        except KeyError:
            raise RuntimeError('unknown task `%s` in flow' % task_id)
        else:
            downstream_tasks = []
            for downstream_idx in downstream_ids:
                try:
                    downstream_tasks.append(tasks[downstream_idx])
                except KeyError:
                    raise RuntimeError('unknown downstream task `%s` for %s'
                                       '' % (downstream_idx, task_id))
            task.set_downstream(downstream_tasks)
