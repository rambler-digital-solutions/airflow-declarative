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

import pytest
from tests.utils import Operator, operator

import airflow_declarative


@pytest.fixture()
def dag(good_dag_path):
    path = good_dag_path("template-defaults")
    dags = airflow_declarative.from_path(path)

    assert len(dags) == 1

    dag = dags[0]

    return dag


def test_callback_params(dag):
    operator0 = dag.task_dict["operator_0"]
    assert operator0.queue == "operators"
    assert operator0._callback == Operator

    operator1 = dag.task_dict["operator_1"]
    assert operator1.queue == "special"
    assert operator1._callback == operator

    sensor = dag.task_dict["sensor"]
    assert sensor.queue == "sensors"
