#!/usr/bin/env python

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

setup(name='synkk',
    version       = '1.0.7',
    description   = 'Syn KnockKnock',
    author        = 'Paul Miller',
    author_email  = 'paul@jettero.pl',
    url           = 'https://github.com/jettero/synkk',
    cmdclass      = {'test': PyTest},
    packages      = find_packages(),

    tests_require = [
        'pytest',
        'pyyaml',
    ],

    install_requires = [
        'click',
        'click-config-file',
        'uptime',
    ],

    entry_points = {
        'console_scripts': [
            'synkk = synkk.cmd:cli',
            'dmesg-synkk-daemon = synkk.daemon:cli',
        ],
    },
)

