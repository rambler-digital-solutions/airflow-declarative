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

from airflow import DAG

import airflow_declarative


def test_integer_callback_arg(good_dag_path):
    path = good_dag_path("integer_callback_arg")
    dags = airflow_declarative.from_path(path)

    assert len(dags) == 1

    yml_dag = dags[0]

    assert isinstance(yml_dag, DAG)

    myoperator = yml_dag.task_dict["myoperator"]
    param = myoperator._callback_args["param"]
    assert isinstance(param, int)
