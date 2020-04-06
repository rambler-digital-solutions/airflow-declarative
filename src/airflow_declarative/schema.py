# -*- coding: utf-8 -*-
#
# Copyright 2017, Rambler Digital Solutions
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import types

import trafaret_config
import yaml

from .trafaret import (
    Any,
    Bool,
    Callback,
    Class,
    Date,
    Dict,
    Email,
    Enum,
    Int,
    Key,
    List,
    Mapping,
    Null,
    OptionalKey,
    String,
    TimeDelta,
    cast_crontab_or_interval,
    cast_interval,
    check_for_class_callback_collisions,
    ensure_callback_args,
)


def from_path(path):
    """Loads schema from YAML file.

    :param str path: YAML file path.
    :returns: Airflow DAGs schema.
    :rtype: dict
    """
    return trafaret_config.read_and_validate(path, SCHEMA)


def ensure_schema(schema):
    """Ensures that schema is valid.

    :param dict schema: Airflow DAGs schema.
    :returns: Airflow DAGs schema.
    :rtype: dict
    """
    return SCHEMA.check(schema)


def dump(schema, *args, **kwargs):
    """Serializes Airflow DAGs schema back to YAML.

    :param dict schema: Airflow DAGs schema.
    :param args: Custom :func:`yaml.dump` args.
    :param kwargs: Custom :func:`yaml.dump` kwargs.
    :returns: YAML content.
    :rtype: str
    """
    kwargs.setdefault("default_flow_style", False)
    kwargs.setdefault("default_style", "")
    return yaml.dump(schema, Dumper=Dumper, *args, **kwargs)


class Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def represent_timedelta(self, delta):
        seconds = delta.seconds
        if not seconds:
            value = "%dd" % delta.days
        elif seconds % 86400 == 0:
            value = "%dd" % (seconds / 86400)
        elif seconds % 3600 == 0:
            value = "%dh" % (seconds / 3600)
        elif seconds % 60 == 0:
            value = "%dm" % (seconds / 60)
        else:
            value = "%ds" % seconds
        return self.represent_scalar("tag:yaml.org,2002:str", value)

    def represent_callable(self, obj):
        value = "%s:%s" % (obj.__module__, obj.__name__)
        return self.represent_scalar("tag:yaml.org,2002:str", value)


Dumper.add_representer(datetime.timedelta, Dumper.represent_timedelta)
Dumper.add_representer(type, Dumper.represent_callable)
Dumper.add_representer(types.FunctionType, Dumper.represent_callable)

# These gives support of dict/list/tuple subclasses serialization like
# namedtuples, trafaret_config.simple.ConfigDict and else.
Dumper.add_multi_representer(dict, Dumper.represent_dict)
Dumper.add_multi_representer(list, Dumper.represent_list)
Dumper.add_multi_representer(tuple, Dumper.represent_list)


ANY = Any()
BOOLEAN = Bool()
CALLBACK = Callback()
CLASS = Class()
DATE = Date()
EMAIL = Email
NULL = Null()
POSITIVE_INT = Int(gte=0)
STRING = String()
TIMEDELTA = TimeDelta()

CRON_PRESETS = Enum("@once", "@hourly", "@daily", "@weekly", "@monthly", "@yearly")
CRONTAB_OR_INTERVAL = (TIMEDELTA | STRING | POSITIVE_INT) >> cast_crontab_or_interval
INTERVAL = (TIMEDELTA | STRING | POSITIVE_INT) >> cast_interval
INTERVAL_INT_SECONDS = (TIMEDELTA | STRING | POSITIVE_INT) >> (
    lambda x: cast_interval(x).total_seconds()
)
PARAMS = Mapping(STRING, ANY)
VERSION = Enum(1)

OPERATOR_ARGS = Dict(
    {
        OptionalKey("adhoc"): BOOLEAN,
        OptionalKey("depends_on_past"): BOOLEAN,
        OptionalKey("do_xcom_push"): BOOLEAN,
        OptionalKey("email"): EMAIL,
        OptionalKey("email_on_failure"): BOOLEAN,
        OptionalKey("email_on_retry"): BOOLEAN,
        OptionalKey("end_date"): DATE,
        OptionalKey("execution_timeout"): INTERVAL,
        OptionalKey("executor_config"): Dict(allow_extra="*"),
        OptionalKey("max_retry_delay"): POSITIVE_INT,
        OptionalKey("on_failure_callback"): CALLBACK,
        OptionalKey("on_retry_callback"): CALLBACK,
        OptionalKey("on_success_callback"): CALLBACK,
        OptionalKey("owner"): STRING,
        OptionalKey("params"): PARAMS,
        OptionalKey("pool"): STRING,
        OptionalKey("priority_weight"): POSITIVE_INT,
        OptionalKey("queue"): STRING,
        OptionalKey("resources"): Dict(
            {
                OptionalKey("cpus"): POSITIVE_INT,
                OptionalKey("disk"): POSITIVE_INT,
                OptionalKey("gpus"): POSITIVE_INT,
                OptionalKey("ram"): POSITIVE_INT,
            }
        ),
        OptionalKey("retries"): POSITIVE_INT,
        OptionalKey("retry_delay"): INTERVAL,
        OptionalKey("retry_exponential_backoff"): BOOLEAN,
        OptionalKey("run_as_user"): STRING,
        OptionalKey("sla"): INTERVAL,
        OptionalKey("start_date"): DATE,
        OptionalKey("task_concurrency"): POSITIVE_INT,
        OptionalKey("trigger_rule"): STRING,
        OptionalKey("wait_for_downstream"): BOOLEAN,
        OptionalKey("weight_rule"): Enum("downstream", "upstream", "absolute"),
    }
)

SENSOR_ARGS = OPERATOR_ARGS + Dict(
    {
        OptionalKey("poke_interval"): INTERVAL_INT_SECONDS,
        OptionalKey("soft_fail"): BOOLEAN,
        OptionalKey("timeout"): POSITIVE_INT,
    }
)

OPERATOR = (
    Dict(
        {
            OptionalKey("class"): CLASS,
            OptionalKey("callback"): CLASS | CALLBACK,
            OptionalKey("callback_args"): PARAMS,
            OptionalKey("args"): (OPERATOR_ARGS + Dict()).allow_extra("*"),
        }
    )
    & check_for_class_callback_collisions
    & ensure_callback_args
)

OPERATORS = Mapping(STRING, OPERATOR)

SENSOR = (
    Dict(
        {
            OptionalKey("class"): CLASS,
            OptionalKey("callback"): CLASS | CALLBACK,
            OptionalKey("callback_args"): PARAMS,
            OptionalKey("args"): (SENSOR_ARGS + Dict()).allow_extra("*"),
        }
    )
    & check_for_class_callback_collisions
    & ensure_callback_args
)

SENSORS = Mapping(STRING, SENSOR)

FLOW = Mapping(key=STRING, value=List(STRING, min_length=1))

DAG_ARGS = Dict(
    {
        OptionalKey("access_control"): Dict(allow_extra="*"),
        OptionalKey("catchup"): BOOLEAN,
        OptionalKey("concurrency"): POSITIVE_INT,
        OptionalKey("dagrun_timeout"): INTERVAL,
        # Sensor args is a superset of all the args.
        OptionalKey("default_args"): SENSOR_ARGS,
        OptionalKey("default_view"): STRING,
        OptionalKey("description"): STRING,
        OptionalKey("doc_md"): STRING,
        OptionalKey("end_date"): DATE,
        OptionalKey("is_paused_upon_creation"): BOOLEAN,
        OptionalKey("jinja_environment_kwargs"): Dict(allow_extra="*"),
        OptionalKey("max_active_runs"): POSITIVE_INT,
        OptionalKey("orientation"): STRING,
        OptionalKey("params"): PARAMS,
        OptionalKey("schedule_interval"): NULL | CRON_PRESETS | CRONTAB_OR_INTERVAL,
        OptionalKey("sla_miss_callback"): CALLBACK,
        OptionalKey("start_date"): DATE,
        OptionalKey("tags"): List(STRING),
    }
)

WITH_ITEMS = List(ANY) | Dict(using=CALLBACK) | Dict(from_stdout=STRING)

DO_TEMPLATE = Dict(
    {
        OptionalKey("operators"): OPERATORS,
        OptionalKey("sensors"): SENSORS,
        OptionalKey("flow"): FLOW,
        Key("with_items"): WITH_ITEMS,
    }
)

DO_TEMPLATES = List(DO_TEMPLATE)

DEFAULTS = Dict({OptionalKey("operators"): OPERATOR, OptionalKey("sensors"): SENSOR})

DAG = Dict(
    {
        OptionalKey("args"): DAG_ARGS,
        OptionalKey("defaults"): DEFAULTS,
        OptionalKey("do"): DO_TEMPLATES,
        OptionalKey("operators"): OPERATORS,
        OptionalKey("sensors"): SENSORS,
        OptionalKey("flow"): FLOW,
    }
)

DAGS = Mapping(key=STRING, value=DAG)

SCHEMA = Dict({Key("dags"): DAGS, OptionalKey("version"): VERSION})
