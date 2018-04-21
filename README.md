# compressed_rtf

[![Build Status](https://travis-ci.org/delimitry/compressed_rtf.svg?branch=master)](https://travis-ci.org/delimitry/compressed_rtf)
[![Coverage Status](https://coveralls.io/repos/github/delimitry/compressed_rtf/badge.svg?branch=master)](https://coveralls.io/github/delimitry/compressed_rtf?branch=master)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/delimitry/compressed_rtf/blob/master/LICENSE)

Compressed Rich Text Format (RTF) compression worker in Python

Description:
------------

Compressed RTF also known as "LZFu" compression format

Based on Rich Text Format (RTF) Compression Algorithm:

https://msdn.microsoft.com/en-us/library/cc463890(v=exchg.80).aspx


Usage example:
--------------

```python
>>> from compressed_rtf import compress, decompress
>>>
>>> data = '{\\rtf1\\ansi\\ansicpg1252\\pard test}'
>>> comp = compress(data, compressed=True)  # compressed
>>> comp
'#\x00\x00\x00"\x00\x00\x00LZFu3\\\xe8t\x03\x00\n\x00rcpg125\x922\n\xf3 t\x07\x90t}\x0f\x10'
>>>
>>> raw = compress(data, compressed=False)  # raw/uncompressed
>>> raw
'.\x00\x00\x00"\x00\x00\x00MELA \xdf\x12\xce{\\rtf1\\ansi\\ansicpg1252\\pard test}'
>>>
>>> decompress(comp)
'{\\rtf1\\ansi\\ansicpg1252\\pard test}'
>>>
>>> decompress(raw)
'{\\rtf1\\ansi\\ansicpg1252\\pard test}'
>>>
```

License:
--------
Released under [The MIT License](https://github.com/delimitry/compressed_rtf/blob/master/LICENSE).
