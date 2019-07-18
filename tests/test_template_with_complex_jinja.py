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

import pytest

import airflow_declarative


@pytest.fixture()
def dag(good_dag_path):
    path = good_dag_path("template-with-complex-jinja")
    dags = airflow_declarative.from_path(path)

    assert len(dags) == 1

    dag = dags[0]

    return dag


def test_callback_params(dag):
    operator = dag.task_dict["operator_2"]
    operator.execute({})
    assert operator._callback_instance.param1 == 7
    assert operator._callback_instance.param2 == 9
    assert operator._callback_instance.param3 == {"a": 7}
