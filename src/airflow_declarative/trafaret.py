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
import importlib
import inspect
import re

import trafaret as t
from croniter import croniter
from trafaret import Any, Bool, Dict, Email, Enum, Int, Key, List, Mapping, Null, String


try:
    from inspect import signature
except ImportError:  # pragma: no cover
    from funcsigs import signature  # noqa


__all__ = (
    "Any",
    "Bool",
    "Callback",
    "Class",
    "Date",
    "Dict",
    "Email",
    "Enum",
    "Int",
    "Key",
    "List",
    "Mapping",
    "Null",
    "OptionalKey",
    "String",
    "TimeDelta",
    "cast_interval",
    "check_for_class_callback_collisions",
    "ensure_callback_args",
)


class OptionalKey(Key):
    def __init__(self, name, **kwargs):
        kwargs.setdefault("optional", True)
        super(OptionalKey, self).__init__(name, **kwargs)


class Date(t.Trafaret):
    def check_and_return(self, value):
        if isinstance(value, datetime.datetime):
            return value
        if not isinstance(value, datetime.date):
            self._failure("value should be a date", value=value)

        time = datetime.datetime.min.time()
        return datetime.datetime.combine(value, time)

    def __repr__(self):
        return "<Date>"


class TimeDelta(t.Trafaret):
    def check_value(self, value):
        if not isinstance(value, datetime.timedelta):
            self._failure("value should be a timedelta", value=value)

    def __repr__(self):
        return "<TimeDelta>"


class Importable(t.Trafaret):
    def check_and_return(self, value):
        if not isinstance(value, str):
            self._failure("value should be a string", value=value)

        if ":" not in value:
            self._failure(
                "import notation must be in format: `package.module:target`",
                value=value,
            )

        module, object_name = value.split(":", 1)

        try:
            mod = importlib.import_module(module)
        except ImportError as exc:
            self._failure(str(exc), value=value)
        else:
            try:
                return getattr(mod, object_name)
            except AttributeError as exc:
                self._failure(str(exc), value=value)

    def __repr__(self):
        return "<Importable>"


class Class(Importable):
    def check_and_return(self, value):
        if inspect.isclass(value):
            return value
        value = super(Class, self).check_and_return(value)
        if not inspect.isclass(value):
            self._failure(
                "imported value should be a class, got %s" % value, value=value
            )
        return value

    def __repr__(self):
        return "<Class>"


class Callback(Importable):
    def check_and_return(self, value):
        if inspect.isfunction(value):
            return value
        value = super(Callback, self).check_and_return(value)
        if not callable(value):
            self._failure(
                "imported value should be a callable, got %s" % value, value=value
            )
        return value

    def __repr__(self):
        return "<Callback>"


def cast_interval(value):
    r"""Casts interval value into `datetime.timedelta` instance.

    If value is `int`, returned `timedelta` get constructed from a given
    by the value`s seconds.

    If value is `str`, then it get converted into seconds according the rules:

    - ``\d+s`` - time delta in seconds. Example: ``10s`` for 10 seconds;
    - ``\d+m`` - time delta in minutes. Example: ``42m`` for 42 minutes;
    - ``\d+h`` - time delta in hours. Example: ``1h`` for 1 hour;
    - ``\d+d`` - time delta in days. Example: ``10d`` for 10 days.

    :param str | int | datetime.timedelta value: An interval value.
    :rtype: datetime.timedelta
    """
    if isinstance(value, str):
        match = re.match(r"^(-)?(\d+)([dhms])$", value)
        if match is not None:
            has_neg_sign, value, unit = match.groups()
            value = int(value)
            value *= {
                # fmt: off
                "s": 1,
                "m": 60,
                "h": 60 * 60,
                "d": 60 * 60 * 24,
                # fmt: on
            }[unit]
            value *= -1 if has_neg_sign else 1
    if isinstance(value, int):
        value = datetime.timedelta(seconds=value)
    elif not isinstance(value, datetime.timedelta):
        raise t.DataError("invalid interval value %s" % value)
    return value


def cast_crontab_or_interval(value):
    try:
        return cast_interval(value)
    except t.DataError:
        if not isinstance(value, str):
            raise
        # This is definitely not a valid time interval.
        # Perhaps this is a cron expression?
        try:
            # Airflow uses `croniter` as well.
            croniter(value)
        except ValueError as e:
            raise t.DataError("Invalid timedelta or crontab expression: %s" % str(e))
        else:
            return value


def check_for_class_callback_collisions(value):
    if "class" in value:
        if "callback" in value or "callback_args" in value:
            raise t.DataError(
                "when `class` specified, there should be no"
                " `callback` and `callback_args`"
            )
    return value


def ensure_callback_args(value):
    callback = value.get("callback")
    if not callback:
        return value

    kwargs = value.get("callback_args", {})
    callback_params = set(kwargs) | {"context"}

    sig = signature(callback)

    required_params = {
        name
        for name, param in sig.parameters.items()
        if param.default is param.empty and param.kind != 2
    }
    missed_params = required_params - callback_params

    if missed_params:
        raise t.DataError(
            "Missed parameters for %s: %s" % (callback, ", ".join(missed_params))
        )

    all_params = {
        name
        for name, param in sig.parameters.items()
        if param.kind != 2  # ignore vararg
    }
    unknown_params = callback_params - all_params

    if unknown_params:
        raise t.DataError(
            "Unexpected parameters for %s: %s" % (callback, ", ".join(unknown_params))
        )

    return value
