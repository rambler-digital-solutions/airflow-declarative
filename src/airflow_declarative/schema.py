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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import trafaret_config

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
    String,
    TimeDelta,
    cast_interval,
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
    return SCHEMA.check_and_return(schema)


ANY = Any()
BOOLEAN = Bool()
CALLBACK = Callback()
CLASS = Class()
DATE = Date()
EMAIL = Email()
POSITIVE_INT = Int(gte=0)
STRING = String()
TIMEDELTA = TimeDelta()

INTERVAL = (TIMEDELTA | STRING | POSITIVE_INT) >> cast_interval
PARAMS = Mapping(STRING, ANY)
VERSION = Enum(1)

OPERATOR_ARGS = Dict(
    adhoc=BOOLEAN,
    depends_on_past=BOOLEAN,
    email=EMAIL,
    email_on_failure=BOOLEAN,
    email_on_retry=BOOLEAN,
    end_date=DATE,
    execution_timeout=INTERVAL,
    max_retry_delay=POSITIVE_INT,
    on_failure_callback=CALLBACK,
    on_retry_callback=CALLBACK,
    on_success_callback=CALLBACK,
    owner=STRING,
    params=PARAMS,
    pool=STRING,
    priority_weight=POSITIVE_INT,
    queue=STRING,
    resources=Dict(
        cpu=POSITIVE_INT,
        disk=POSITIVE_INT,
        gpus=POSITIVE_INT,
        ram=POSITIVE_INT,
    ).make_optional('*'),
    retries=POSITIVE_INT,
    retry_delay=INTERVAL,
    retry_exponential_backoff=BOOLEAN,
    run_as_user=STRING,
    sla=INTERVAL,
    start_date=DATE,
    trigger_rule=STRING,
    wait_for_downstream=BOOLEAN,
).make_optional('*')

SENSOR_ARGS = OPERATOR_ARGS + Dict(
    poke_interval=INTERVAL,
    soft_fail=BOOLEAN,
    timeout=POSITIVE_INT,
).make_optional('*')

OPERATOR = Dict({
    Key('class'): CLASS,
    Key('args'): OPERATOR_ARGS.allow_extra('*'),
}).make_optional('args')

OPERATORS = Mapping(STRING, OPERATOR)

SENSOR = Dict({
    Key('class'): CLASS,
    Key('args'): SENSOR_ARGS.allow_extra('*'),
}).make_optional('args')

SENSORS = Mapping(STRING, SENSOR)

FLOW = Mapping(
    key=STRING,
    value=List(STRING, min_length=1)
)

DAG_ARGS = Dict(
    catchup=BOOLEAN,
    concurrency=POSITIVE_INT,
    dagrun_timeout=INTERVAL,
    default_args=SENSOR_ARGS,  # Sensor args is a superset of all the args.
    description=STRING,
    end_date=DATE,
    max_active_runs=POSITIVE_INT,
    orientation=STRING,
    schedule_interval=INTERVAL,
    sla_miss_callback=CALLBACK,
    start_date=DATE,
).make_optional('*')

DAG = Dict(
    args=DAG_ARGS,
    operators=OPERATORS,
    sensors=SENSORS,
    flow=FLOW,
).make_optional('*')

DAGS = Mapping(
    key=STRING,
    value=DAG,
)

SCHEMA = Dict(
    dags=DAGS,
    version=VERSION,
).make_optional('version')
