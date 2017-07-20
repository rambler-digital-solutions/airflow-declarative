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

from . import builder, schema


__all__ = (
    'from_path',
    'from_dict',
)


def from_path(path):
    """Loads DAGs from a full path to YAML file.

    :param str path: YAML file path.
    :rtype: list[airflow.DAG]
    """
    return from_dict(schema.from_path(path))


def from_dict(schema):
    """

    :param dict schema:
    :rtype: list[airflow.DAG]
    """
    return builder.build_dags(schema)
