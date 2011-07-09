#
# Copyright (c) 2011 Daniel Truemper truemped@googlemail.com
#
# setup.py 06-Jul-2011
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
# under the License.
#
from setuptools import setup, find_packages

tests_require = ['coverage>=3.4']

setup(
    name = "tornadotools",
    version = '0.1',
    description = "A set of tools for working with tornado",
    author = "Daniel Truemper",
    author_email = "trueped@googlemail.com",
    url = "https://github.com/truemped/tornadotools",
    packages = find_packages(),
    include_package_data = True,
    test_suite = 'nose.collector',
    install_requires = [
        'tornado>=1.2',
        'pycurl>=7.19.0',
    ],
    tests_require = tests_require,
    extras_require = {
        'test': tests_require,
        'mongrel2': ['pyzmq>=2.1.7','tnetstring>=0.2.0'],
    },
    entry_points = {
        'console_scripts' : [
        ]
    }
)
