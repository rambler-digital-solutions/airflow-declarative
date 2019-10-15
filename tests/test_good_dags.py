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

import os

import airflow
import yaml

import airflow_declarative
import airflow_declarative.schema

from .utils import list_examples


def param_id(param):
    return os.path.splitext(os.path.basename(param))[0]


def pytest_generate_tests(metafunc):
    parameters = list_examples("good")
    metafunc.parametrize("path", parameters, ids=param_id)


def test_good_dags(path):
    dags = airflow_declarative.from_path(path)
    assert isinstance(dags, list)
    assert all(isinstance(dag, airflow.DAG) for dag in dags)


def test_serde(path):
    schema0 = airflow_declarative.transform(airflow_declarative.schema.from_path(path))
    content = airflow_declarative.render(path)
    schema1 = airflow_declarative.schema.ensure_schema(yaml.load(content))
    assert schema0 == schema1
