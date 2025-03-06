#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup file, used to install and test 'compressed_rtf'
"""

import os
from setuptools import setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "compressed_rtf", "__version__.py"), "r", encoding = "utf-8") as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    description=about["__description__"],
    long_description=about["__long_description__"],
    license=about["__license__"],
    keywords='compressed-rtf lzfu mela rtf',
    url=about["__url__"],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing',
        'Topic :: System :: Archiving :: Compression',
    ],
)
