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

from datetime import date

import pytest
from airflow.operators.bash_operator import BashOperator
from tests.utils import MultiParamOperator, Operator, sensor

import airflow_declarative


@pytest.fixture()
def dag(good_dag_path):
    path = good_dag_path("template-with-invalid-schema-before-do")
    dags = airflow_declarative.from_path(path)

    assert len(dags) == 1

    dag = dags[0]

    return dag


def test_callback_params(dag):
    operator_multi = dag.task_dict["operator_multi"]
    assert operator_multi._callback == MultiParamOperator
    assert operator_multi._callback_args == {
        "param1": "egg",
        "param2": "bacon",
        "param3": "spam",
    }

    operator_simple = dag.task_dict["operator_simple"]
    assert operator_simple._callback == Operator
    assert operator_simple._callback_args == {"param": "egg"}

    operator_bash = dag.task_dict["operator_bash"]
    assert isinstance(operator_bash, BashOperator)
    assert operator_bash.bash_command == 'echo "test"'
    assert operator_bash.end_date == date(2019, 10, 25)

    sensor_simple = dag.task_dict["sensor_simple"]
    assert sensor_simple._callback == sensor
