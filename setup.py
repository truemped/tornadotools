#
# Copyright (c) 2011 Retresco GmbH
#
# setup.py 01-Apr-2011
#
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
    extras_require = {'test': tests_require},
    entry_points = {
        'console_scripts' : [
        ]
    }
)
