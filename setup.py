#!/usr/bin/env python3

from setuptools import setup
import os
import sys

if sys.version_info < (3, 2, 0):
    raise Exception("Only python 3.2+ is supported")

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

exec(read("cses/version.py"))

setup(
    name = "cses",
    version = __version__,
    description = "Code Submission Evaluation System client",
    long_description = read("README.rst"),
    author = "Juhani Imberg",
    author_email = "juhani@imberg.fi",
    url = "https://github.com/JuhaniImberg/cses.py",
    license = "MIT",
    packages = ["cses", "cses.commands", "cses.tasks"],
    entry_points = {
        "console_scripts": [
            "cses=cses.cli:cli"
        ]
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ],
    install_requires = [
        "click == 3.3",
        "requests == 2.5.1"
    ]
)
