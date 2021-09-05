..
.. Copyright 2019, Rambler Digital Solutions
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
.. http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
..


Declarative DAG Reference
=========================

The actual schema definition can be found in the `airflow_declarative/schema.py`_
module. Some examples of complete DAGs are also available in
the `tests/dags/good`_ directory.

.. _airflow_declarative/schema.py: https://github.com/rambler-digital-solutions/airflow-declarative/blob/master/src/airflow_declarative/schema.py
.. _tests/dags/good: https://github.com/rambler-digital-solutions/airflow-declarative/tree/master/tests/dags/good

This document contains a verbose description of the declarative DAG schema.

The anatomy of a declarative DAG:

.. code-block:: yaml
    :linenos:

    # The comments below specify the names of the schema definition
    # atoms which can be found in the `airflow_declarative/schema.py`
    # module.

    dags:
      my_dag:  # the DAG name

        defaults:
          sensors:
            # `SENSOR`
            args:
              # `SENSOR_ARGS`
              queue: my_sensors_queue
          operators:
            # `OPERATOR`
            args:
              # `OPERATOR_ARGS`
              queue: my_operators_queue

        args:
          # `DAG_ARGS`
          start_date: 2019-07-01
          schedule_interval: 1d
          default_args:
            # `SENSOR_ARGS` | `OPERATOR_ARGS`
            owner: my_name

        sensors:
          my_sensor:
            # `SENSOR`
            callback: myproject.mymodule:my_sensor_callback
            callback_args:
              my_kwarg: my_value
            args:
              # `SENSOR_ARGS`
              poke_interval: 1m

        operators:
          my_operator:
            # `OPERATOR`
            callback: myproject.mymodule:my_operator_callback
            callback_args:
              my_kwarg: my_value
            args:
              # `OPERATOR_ARGS`
              retries: 3

        flow:
          # `FLOW`
          my_sensor:
          - my_operator

        do:
        # `DO_TEMPLATE`
        - operators:
            my_crops_{{ item.name }}:
              # `OPERATOR`
              callback: myproject.myfruits:my_crops
              callback_args:
                fruit: '{{ item.fruit_props }}'
          # `sensors` can be used there too!
          flow:
            # `FLOW`
            my_operator:
            - my_crops_{{ item.name }}
          with_items:
          # `WITH_ITEMS`
          - name: pineapple
            fruit_props:
              shape: ellipsoid
              color: brown
          - name: watermelon
            fruit_props:
              shape: round
              color: green


.. TODO maybe add the Python equivalent of that declarative DAG?

DAG_ARGS
--------

``DAG_ARGS`` atom defines the ``__init__`` arguments of an Airflow DAG.
The actual meaning of these args can be found in the :class:`airflow.models.DAG`
doc page.


.. _operator_sensor:

OPERATOR / SENSOR
-----------------

``OPERATOR`` and ``SENSOR`` atoms look similarly, except that their ``args``
schemas are different. They both define an Airflow operator (note that Sensors
in Airflow are considered to be Operators).

For an Operator, the ``args`` (the ``OPERATOR_ARGS`` atom) are
the ``__init__`` args of the :class:`airflow.models.BaseOperator`.

For a Sensor, the ``args`` (the ``SENSOR_ARGS`` atom) are
the ``__init__`` args of
the :class:`airflow.sensors.base.BaseSensorOperator`.

The ``OPERATOR``/``SENSOR`` callable might be specified as a class.
Example for :class:`airflow.operators.bash.BashOperator`:

.. code-block:: yaml

    class: airflow.operators.bash:BashOperator
    args:
      bash_command: 'echo "Hello World {{ ds }}"'

... or as a Python callable:

.. code-block:: yaml

    callback: myproject.mymodule:my_operator_callback
    callback_args:
      my_kwarg: my_value
    args:
      retries: 3

If ``callback`` value is a function, then it should look like this::

    def my_operator_callback(context, my_kwarg):
        print("Execution date", conext["ds"])
        print("my_kwarg", my_kwarg)

The ``callback`` might also be a class::

    class MyOperatorCallback:
        def __init__(self, context, my_kwarg):
            self.ds = context["ds"]
            self.my_kwarg = my_kwarg

        def __call__(self):
            print("Execution date", self.ds)
            print("my_kwarg", self.my_kwarg)


``callback_args`` key is relevant only when ``callback`` is used (i.e. it cannot
be defined with ``class``). The distinction between the ``args`` and
the ``callback_args`` is simple:

- ``args`` are the ``__init__`` args for the :class:`airflow.models.BaseOperator`,
  which is used under the hood to wrap the ``callback``;
- ``callback_args`` are the additional kwargs which would be passed to
  the ``callback`` along with the task ``context``.


default_args / defaults
-----------------------

``default_args`` is a standard :class:`airflow.models.DAG` ``__init__``
arg which specifies the default args of a :class:`airflow.models.BaseOperator`.
These args would be supplied to all DAG's operators and sensors.

The ``defaults`` dict is a Declarative's extension which allows to specify
the args more granularly: only to ``sensors`` or only to ``operators``
(note that defaults specified in ``operators`` would not be applied
to sensors).


.. _flow:

FLOW
----

The ``FLOW`` atom defines the DAG links between the operators.

``FLOW`` is a dict of lists, where a key is a downstream operator name,
and a value is a list of upstream operators.

Consider the following flow:

.. code-block:: yaml

    my_sensor:
    - my_task_1
    - my_task_2

    my_task_1:
    - my_task_3

Assuming that the Airflow operators are assigned to variables, the Python
equivalent would be:

.. code-block:: python

    my_sensor.set_upstream(my_task_1)
    my_sensor.set_upstream(my_task_2)

    my_task_1.set_upstream(my_task_3)

This would be rendered in the Airflow web-interface like this:

- Tree view:

    .. image:: ./_static/flow_tree_view.png
        :width: 300

- Graph view:

    .. image:: ./_static/flow_graph_view.png
        :width: 300


DO (with_items)
---------------

The ``do`` block allows to make the DAG schema dynamic.

A ``do`` value is a list of dicts, each dict (a ``DO_TEMPLATE``) must
contain a ``with_items`` key and might optionally contain ``operators``,
``sensors`` and ``flow`` -- these have the same schema as the corresponding
keys of the DAG.

``with_items`` defines a list of items, which should be used to render
a single ``DO_TEMPLATE`` block. Operators, Sensors and Flow within the block
would be merged together (as dict unions).

There're 3 different ways to define ``with_items``:

1. As a static list of items:

    .. code-block:: yaml

          with_items:
          - some_name: John
          - some_name: Jill

2. As a Python callback, which returns a list of items:

    .. code-block:: yaml

          with_items:
            using: myproject.mymodule:my_with_items

    Where ``my_with_items`` is a Python function which might look like this::

        def my_with_items():
            return [
                {"some_name": "John"},
                {"some_name": "Jill"},
            ]

3. As an external program, which prints to stdout a list of items in JSON:

    .. code-block:: yaml

          with_items:
            from_stdout: my_command --my-arg 42

    Where ``my_command`` is an executable in ``$PATH``, which might look like this::

        #!/usr/bin/env ruby

        require 'json'

        print [
          {some_name: "John"},
          {some_name: "Jill"},
        ].to_json

``operators``, ``sensors`` and ``flow`` within the ``DO_TEMPLATE`` block
should use Jinja2 templates to render the items.

The following DAG defined by a ``do`` block:

.. code-block:: yaml

    operators:
      my_operator:
        callback: myproject.mymodule:my_operator_callback
    do:
    - operators:
        my_crops_{{ item.name }}:
          callback: myproject.myfruits:my_crops
          callback_args:
            fruit: '{{ item.fruit_props }}'
      flow:
        my_operator:
        - my_crops_{{ item.name }}
      with_items:
      - name: pineapple
        fruit_props:
          shape: ellipsoid
          color: brown
      - name: watermelon
        fruit_props:
          shape: round
          color: green


... is equivalent to the following DAG defined statically:

.. code-block:: yaml

    operators:
      my_operator:
        callback: myproject.mymodule:my_operator_callback
      my_crops_pineapple:
        callback: myproject.myfruits:my_crops
        callback_args:
          fruit:
            shape: ellipsoid
            color: brown
      my_crops_watermelon:
        callback: myproject.myfruits:my_crops
        callback_args:
          fruit:
            shape: round
            color: green
    flow:
     my_operator:
     - my_crops_pineapple
     - my_crops_watermelon
