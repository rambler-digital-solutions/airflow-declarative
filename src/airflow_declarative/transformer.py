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

import json
import shlex
import subprocess
import sys
from itertools import chain

import jinja2
import yaml
from jinja2.ext import Extension
from jinja2.lexer import Token
from trafaret import str_types

from .compat import Iterable, Mapping
from .schema import dump, ensure_schema


try:
    from functools import reduce
except ImportError:
    pass


def yaml_filter(obj):
    if isinstance(obj, str_types):
        return obj
    elif isinstance(obj, jinja2.Undefined):
        return ""
    else:
        try:
            return dump(obj)
        except Exception as exc:
            raise RuntimeError(
                "Unable to serialize {!r} to YAML because {}."
                "Template render must produce valid YAML file, so please use"
                " simple types in `with_items` block."
                "".format(obj, exc)
            )


class YamlExtension(Extension):
    def filter_stream(self, stream):
        """
        We convert
        {{ some.variable | filter1 | filter 2}}
            to
        {{ some.variable | filter1 | filter 2 | yaml}}

        ... for all variable declarations in the template

        This function is called by jinja2 immediately
        after the lexing stage, but before the parser is called.
        """
        while not stream.eos:
            token = next(stream)
            if token.test("variable_begin"):
                var_expr = []
                while not token.test("variable_end"):
                    var_expr.append(token)
                    token = next(stream)
                variable_end = token

                last_token = var_expr[-1]
                if last_token.test("name") and last_token.value == "yaml":
                    # don't yaml twice
                    continue

                # Wrap the whole expression between the `variable_begin`
                # and `variable_end` marks in parens:
                var_expr.insert(1, Token(var_expr[0].lineno, "lparen", None))
                var_expr.append(Token(var_expr[-1].lineno, "rparen", None))

                var_expr.append(Token(token.lineno, "pipe", "|"))
                var_expr.append(Token(token.lineno, "name", "yaml"))

                var_expr.append(variable_end)

                for token in var_expr:
                    yield token
            else:
                yield token


ENV = jinja2.Environment()
ENV.filters["yaml"] = yaml_filter
ENV.add_extension(YamlExtension)


def transform(schema):
    schema0 = ensure_schema(schema)
    schema1 = transform_templates(schema0)
    schema2 = transform_defaults(schema1)
    return schema2


def transform_templates(schema):
    for dag_id, dag_schema in schema["dags"].items():
        if "do" not in dag_schema:
            continue
        templates = dag_schema.pop("do")
        for template in templates:
            transform_strategy(dag_schema, template)
    return schema


def transform_strategy(schema, template):
    if "with_items" in template:
        return transform_with_items(schema, template)
    else:
        raise RuntimeError("cannot figure how to apply template: {}".format(template))


def transform_with_items(schema, template):
    items = template["with_items"]
    if isinstance(items, dict):
        if set(items) == {"using"}:
            items = items["using"]
        elif set(items) == {"from_stdout"}:
            items = from_stdout(items["from_stdout"])
    if hasattr(items, "__call__"):
        items = items()
    if not isinstance(items, Iterable):
        raise RuntimeError("bad with_items template: {}".format(items))
    for key in {"operators", "sensors", "flow"}:
        if key not in template:
            continue
        subschema = reduce(merge, transform_schema_with_items(template[key], items), {})
        schema.setdefault(key, {})
        schema[key] = merge(schema[key], subschema)
    return schema


def from_stdout(cmd):
    PY2 = sys.version_info[0] == 2
    if PY2:
        cmd = cmd.encode("utf8")
    output = subprocess.check_output(shlex.split(cmd))
    if not PY2:
        output = output.decode("utf8")
    return json.loads(output)


def transform_schema_with_items(schema, items):
    return [transform_dict_with_item(schema, item) for item in items]


def transform_value_with_item(value, item):
    if isinstance(value, Mapping):
        return transform_dict_with_item(value, item)
    elif isinstance(value, str_types):
        return transform_string_with_item(value, item)
    elif isinstance(value, Iterable):
        return transform_list_with_item(value, item)
    else:
        return value


def transform_dict_with_item(dict, item):
    result = {}
    for key, value in dict.items():
        key = transform_value_with_item(key, item)
        value = transform_value_with_item(value, item)
        result[key] = value
    return result


def transform_list_with_item(list, item):
    return [transform_value_with_item(value, item) for value in list]


def transform_string_with_item(string, item, env=ENV):
    # That's not very cool, but at least this ensures that users won't send
    # us arbitrary objects and will stay withof simple and clean data types.
    return yaml.safe_load(env.from_string(string).render(item=item))


def merge(base, other):
    if isinstance(base, Mapping) and isinstance(other, Mapping):
        return merge_mappings(base, other)
    elif isinstance(base, str_types) and isinstance(other, str_types):
        return base
    elif isinstance(base, Iterable) and isinstance(other, Iterable):
        return merge_iterable(base, other)
    else:
        return base


def merge_mappings(base, other):
    result = dict(**base)
    for key in other:
        if key not in base:
            result[key] = other[key]
        elif base[key] == other[key]:
            continue
        else:
            result[key] = merge(base[key], other[key])
    return result


def merge_iterable(base, other):
    return list(chain(base, other))


def transform_defaults(schema):
    for dag_id, dag_schema in schema["dags"].items():
        defaults = dag_schema.pop("defaults", {})
        if not defaults:
            continue
        for key in {"sensors", "operators"}:
            if key in dag_schema and key in defaults:
                transform_apply_tasks_defaults(dag_schema[key], defaults[key])
    return schema


def transform_apply_tasks_defaults(tasks, defaults):
    for task_id, task_schema in tasks.items():
        tasks[task_id] = transform_apply_task_defaults(task_schema, defaults)


def transform_apply_task_defaults(task, defaults):
    return merge_mappings(task, defaults)
