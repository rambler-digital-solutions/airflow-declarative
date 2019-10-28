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

from . import builder, schema, transformer


__all__ = ("from_path", "from_dict", "render")


def from_path(path, check_imports=True):
    """Load DAGs from a YAML file.

    :param str path: A path to the declarative YAML file.
    :param bool check_imports: Whether or not check importable objects
    :rtype: list[airflow.models.DAG]
    """
    return from_dict(
        schema.from_path(path, check_imports=check_imports), check_imports=check_imports
    )


def from_dict(schema, check_imports=True):
    """Load DAGs from a dict (i.e. the parsed YAML file contents).

    :param dict schema: The declarative YAML schema.
    :param bool check_imports: Whether or not check importable objects
    :rtype: list[airflow.models.DAG]
    """
    return builder.build_dags(
        transform(schema, check_imports=check_imports), check_imports=check_imports
    )


def transform(schema, check_imports=True):
    """Preprocess the declarative YAML schema:
    - validate the schema,
    - expand the `do` block,
    - expand `defaults`.

    :param dict schema: The declarative YAML schema.
    :param bool check_imports: Whether or not check importable objects
    :rtype: dict
    """
    return transformer.transform(schema, check_imports=check_imports)


def render(path, check_imports=True):
    """Return the transformed schema in yaml format. Useful for debugging.

    :param str path: A path to the declarative YAML file.
    :param bool check_imports: Whether or not check importable objects
    :rtype: str
    """
    return schema.dump(
        transform(
            schema.from_path(path, check_imports=check_imports),
            check_imports=check_imports,
        )
    )
