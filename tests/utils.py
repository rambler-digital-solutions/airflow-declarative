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

import os


def examples_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "dags"))


def list_examples(kind):
    root = os.path.join(examples_path(), kind)
    return [
        os.path.join(root, item)
        for item in os.listdir(root)
        if item.endswith((".yaml", ".yml"))
    ]


def noop_callback(*args, **kwargs):
    pass


def operator(context):
    pass


def sensor(context):
    return True


def gen_items():
    return range(3)


class Operator(object):
    def __init__(self, context, param):
        self.context = context
        self.param = param

    def __call__(self):
        pass


class MultiParamOperator(object):
    def __init__(self, context, param1=None, param2=None, param3=None):
        self.context = context
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3

    def __call__(self):
        pass


class Sensor(object):
    def __init__(self, context, param):
        self.context = context
        self.param = param

    def __call__(self):
        return True
