#!/usr/bin/env python
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

from setuptools import find_packages, setup
from setuptools.command.sdist import sdist as sdist_orig


ROOT_DIR = os.path.dirname(__file__)
README_PATH = os.path.join(ROOT_DIR, 'README.rst')
VERSION_PATH = os.path.join(ROOT_DIR, 'VERSION')


if os.path.exists(VERSION_PATH):
    with open(VERSION_PATH) as verfile:
        __version__ = verfile.read().strip()
else:
    __version__ = os.popen('git describe --tags --always').read().strip()
    try:
        base, distance, commit_hash = __version__.split('-')
    except ValueError:
        # We're on release tag.
        pass
    else:
        # Reformat git describe for PEP-440
        __version__ = '{}.{}+{}'.format(base, distance, commit_hash)
if not __version__:
    # However, things can go wrong, so we'll cry for help here.
    raise RuntimeError('cannot detect project version')


class sdist(sdist_orig):

    def run(self):
        with open(VERSION_PATH, 'w') as fobj:
            fobj.write(__version__)
        sdist_orig.run(self)


with open(README_PATH) as f:
    long_story = f.read()


setup(
    name='airflow-declarative',
    version=__version__,
    description='Airflow DAGs done declaratively',
    long_description=long_story,
    license='Apache 2.0',

    author='Usermodel Team @ Rambler Digital Solutions',
    author_email='um@rambler-co.ru',
    maintainer='Alexander Shorin',
    maintainer_email='kxepal@gmail.com',

    url='https://github.com/rambler-digital-solutions/airflow-declarative',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],

    package_dir={'': 'src'},
    packages=find_packages('src'),

    install_requires=[
        'apache-airflow',

        'croniter',
        'funcsigs; python_version<"3"',
        'jinja2>=2.8',
        'trafaret-config==1.0.1',
        'trafaret<2,>=1.0',
    ],
    extras_require={
        'develop': [
            'flake8==3.5.0',
            'isort==4.3.4',
            'mock==2.0.0',
            'pylint==2.3.1; python_version>="3"',
            'pytest-cov==2.6.0',
            'pytest-sugar==0.9.1',
            'pytest==3.8.2',
            'sphinx-rtd-theme>=0.4.2',
            'sphinx==1.8.1',
        ],
    },

    cmdclass={
        'sdist': sdist
    },
)
