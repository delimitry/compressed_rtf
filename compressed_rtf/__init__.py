# -*- coding: utf-8 -*-

"""
Compressed Rich Text Format (RTF) compression and decompression package

Based on Rich Text Format (RTF) Compression Algorithm
https://msdn.microsoft.com/en-us/library/cc463890(v=exchg.80).aspx
"""

from .compressed_rtf import compress, decompress
from .version import __version__

__all__ = ['compress', 'decompress', '__version__']
