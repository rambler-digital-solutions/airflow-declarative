# -*- coding: utf-8 -*-
#
# Copyright 2019, Rambler Digital Solutions
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

import datetime

from airflow import DAG

import airflow_declarative


try:
    # Since Airflow 1.10
    from airflow.sensors.time_delta_sensor import TimeDeltaSensor
except ImportError:
    from airflow.operators.sensors import TimeDeltaSensor


def test_timedelta_sensor(good_dag_path):
    path = good_dag_path("timedelta-sensor")
    dags = airflow_declarative.from_path(path)

    assert len(dags) == 1

    yml_dag = dags[0]

    assert isinstance(yml_dag, DAG)

    expected_tasks = {
        "dummy_operator",
        "timedelta_sensor",
        "dynamic_timedelta_sensor_1h",
    }
    assert set(yml_dag.task_ids) == expected_tasks

    timedelta_sensor = yml_dag.task_dict["timedelta_sensor"]
    assert isinstance(timedelta_sensor, TimeDeltaSensor)
    assert isinstance(timedelta_sensor.delta, datetime.timedelta)
    assert 6 == timedelta_sensor.delta.hours

    dynamic_timedelta_sensor_1h = yml_dag.task_dict["dynamic_timedelta_sensor_1h"]
    assert isinstance(dynamic_timedelta_sensor_1h, TimeDeltaSensor)
    assert isinstance(dynamic_timedelta_sensor_1h.delta, datetime.timedelta)
    assert 1 == dynamic_timedelta_sensor_1h.delta.hours
