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

import inspect
import itertools
import os

import airflow.exceptions
import pytest
import trafaret_config

import airflow_declarative


# fmt: off
text_type = type(u"")  # six.text_type
# fmt: on


def param_id(param):
    if inspect.isclass(param):
        return param.__name__
    elif isinstance(param, text_type):
        return os.path.splitext(os.path.basename(param))[0]
    else:
        return None  # Let pytest use its default id generator


def examples_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "dags"))


def list_examples(kind):
    root = os.path.join(examples_path(), kind)
    return [
        os.path.join(root, item)
        for item in os.listdir(root)
        if item.endswith((".yaml", ".yml"))
    ]


def pytest_generate_tests(metafunc):
    parameters = itertools.chain.from_iterable(
        [
            zip(
                list_examples("schema-errors"),
                itertools.repeat(trafaret_config.ConfigError),
            ),
            zip(
                list_examples("logic-errors"),
                itertools.repeat(
                    (RuntimeError, TypeError, airflow.exceptions.AirflowException)
                ),
            ),
            zip(
                list_examples("airflow-errors"),
                itertools.repeat(airflow.exceptions.AirflowException),
            ),
        ]
    )
    metafunc.parametrize("path, expected_exception", parameters, ids=param_id)


def test_bad_dags(path, expected_exception):
    with pytest.raises(expected_exception):
        airflow_declarative.from_path(path)
