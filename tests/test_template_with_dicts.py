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

import airflow_declarative
from airflow_declarative.operators import GenericOperator


@pytest.fixture()
def dag(good_dag_path):
    path = good_dag_path("template-with-dicts")
    dags = airflow_declarative.from_path(path)

    assert len(dags) == 1

    dag = dags[0]

    return dag


def test_callback_params(dag):
    foo = dag.task_dict["operator_foo"]
    assert isinstance(foo, GenericOperator)
    foo.execute({})
    assert foo._callback_instance.param == {"hello": ["привет"]}

    bar = dag.task_dict["operator_bar"]
    assert isinstance(bar, GenericOperator)
    bar.execute({})
    assert bar._callback_instance.param == {"world": ["мир"]}

    baz = dag.task_dict["operator_baz"]
    assert isinstance(baz, GenericOperator)
    baz.execute({})
    assert baz._callback_instance.param == {"qwerty": ["йцукен"]}

    assert set(dag.task_dict) == {
        "operator_foo",
        "operator_bar",
        "operator_baz",
        "sensor",
    }
