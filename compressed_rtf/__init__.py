# -*- coding: utf-8 -*-

"""
Compressed Rich Text Format (RTF) compression and decompression package

Based on Rich Text Format (RTF) Compression Algorithm
https://msdn.microsoft.com/en-us/library/cc463890(v=exchg.80).aspx
"""

__title__ = 'compressed_rtf'
__version__ = '1.0.6'
__author__ = 'Dmitry Alimov'
__license__ = 'MIT'

from .compressed_rtf import compress, decompress
