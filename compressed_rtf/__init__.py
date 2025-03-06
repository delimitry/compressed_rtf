# -*- coding: utf-8 -*-

"""
Compressed Rich Text Format (RTF) compression and decompression package

Based on Rich Text Format (RTF) Compression Algorithm
https://msdn.microsoft.com/en-us/library/cc463890(v=exchg.80).aspx
"""

from .__version__ import (
    __author__,
    __description__,
    __license__,
    __long_description__,
    __title__,
    __url__,
    __version__,
)

from .compressed_rtf import compress, decompress
