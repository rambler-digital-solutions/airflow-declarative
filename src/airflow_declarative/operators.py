# -*- coding: utf-8 -*-
#
# Copyright 2017, Rambler&Co
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

from airflow.utils.decorators import apply_defaults

from .compat import BaseOperator, BaseSensorOperator


class CallbackMixIn(object):
    _callback = None
    _callback_instance = None

    def __init__(self, callback, args):
        assert callable(callback), callback
        self._callback = callback
        self._callback_args = args

    def _call_callback(self, context):
        kwargs = self._callback_args
        if self._callback_instance is not None:
            return self._callback_instance()
        elif inspect.isclass(self._callback):
            self._callback_instance = self._callback(context, **kwargs)
            return self._callback_instance()
        else:
            return self._callback(context, **kwargs)


class GenericOperator(BaseOperator, CallbackMixIn):
    """Generic operator to wrap and call the callback function which implements
    all the logic without being associated with airflow anyhow except by
    context.
    """

    @apply_defaults
    def __init__(self, _callback, _callback_args, *args, **kwargs):
        CallbackMixIn.__init__(self, _callback, _callback_args)
        super(GenericOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        return self._call_callback(context)


class GenericSensor(BaseSensorOperator, CallbackMixIn):
    """Generic sensor to wrap and call the callback function which implements
    all the logic without being associated with airflow anyhow except by
    context.
    """

    @apply_defaults
    def __init__(self, _callback, _callback_args, *args, **kwargs):
        CallbackMixIn.__init__(self, _callback, _callback_args)
        super(GenericSensor, self).__init__(*args, **kwargs)

    def poke(self, context):
        rval = self._call_callback(context)
        if rval is None:
            raise RuntimeError(
                "Sensor call returned None. It seems like"
                " a mistake as it may never complete."
                " Return boolean back please."
            )
        return bool(rval)
