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

import mock
import pytest

import airflow_declarative
from airflow_declarative.operators import GenericOperator, GenericSensor


@pytest.fixture()
def dag(good_dag_path):
    path = good_dag_path("callback-tasks")
    dags = airflow_declarative.from_path(path)

    assert len(dags) == 1

    dag = dags[0]

    return dag


def test_callbacks(dag):
    sensor_class = dag.task_dict["sensor_class"]
    assert isinstance(sensor_class, GenericSensor)
    assert sensor_class.poke({}) is True
    assert sensor_class._callback_instance.param == "something"

    sensor_func = dag.task_dict["sensor_func"]
    assert isinstance(sensor_func, GenericSensor)
    assert sensor_func.poke({}) is True
    assert sensor_func.poke_interval == 10.0

    worker = dag.task_dict["worker"]
    assert isinstance(worker, GenericOperator)
    assert worker.execute({}) is None


def test_sensor_returns_none(dag):
    sensor = dag.task_dict["sensor_func"]
    assert isinstance(sensor, GenericSensor)

    with mock.patch.object(sensor, "_callback", lambda ctx: None):
        with pytest.raises(RuntimeError):
            assert sensor.poke({}) is not None


def test_class_tasks_calls_multiple_times(dag):
    sensor = dag.task_dict["sensor_class"]
    assert isinstance(sensor, GenericSensor)

    with mock.patch.object(sensor._callback, "__call__", return_value=True) as patch:
        sensor.poke({})
        sensor.poke({})
        assert patch.call_count == 2
        patch.assert_called_with()
