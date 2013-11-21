#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import sys
import os.path

def long_description():
    with open(os.path.join(os.path.dirname(__file__), "README.rst")) as f:
        return f.read()

def classifiers():
    if sys.version < '2.2.3':
        return None
    return [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Text Processing :: Markup :: HTML',
            ]

setup(
    name="prodigal",
    version="0.1",
    description="Static website generator for Jinja2 templates",
    long_description=long_description(),
    author="Régis Behmo",
    author_email="regis@behmo.com",
    url="https://github.com/regisb/prodigal",
    packages=["prodigal"],
    scripts=["prodigal/prodigal"],
    install_requires=["Jinja2", "babel"],
    license="BSD",
    classifiers=classifiers()
)
