#!/usr/bin/env python
#-*- coding: utf8 -*-

import unittest
from compressed_rtf import compress, decompress
from crc32 import crc32


class Test(unittest.TestCase):
    """
    Test RTF compression and decompression
    """

    def test_decompress(self):
        """
        Test decompression
        """
        data = '-\x00\x00\x00+\x00\x00\x00LZFu\xf1\xc5\xc7\xa7\x03\x00\n\x00' \
            'rcpg125B2\n\xf3 hel\t\x00 bw\x05\xb0ld}\n\x80\x0f\xa0'
        self.assertEqual(
            decompress(data),
            '{\\rtf1\\ansi\\ansicpg1252\\pard hello world}\r\n')
        # test raw decompression
        data = '.\x00\x00\x00"\x00\x00\x00MELA \xdf\x12\xce{\\rtf1\\ansi\\an' \
            'sicpg1252\\pard test}'
        self.assertEqual(
            decompress(data),
            '{\\rtf1\\ansi\\ansicpg1252\\pard test}')

    def test_crc32(self):
        """
        Test CRC32 computation
        """
        data = '\x03\x00\n\x00rcpg125B2\n\xf3 hel\t\x00 bw\x05\xb0ld}\n\x80' \
            '\x0f\xa0'
        self.assertEqual(crc32(data), 0xa7c7c5f1)
        # test empty crc32
        self.assertEqual(crc32(''), 0x00000000)

    def test_compression(self):
        """
        Test compression types compressed and uncompressed
        """
        data = '{\\rtf1\\ansi\\ansicpg1252\\pard hello world}\r\n'
        self.assertEqual(
            compress(data, compressed=True),
            '-\x00\x00\x00+\x00\x00\x00LZFu\xf1\xc5\xc7\xa7\x03\x00\n\x00'
            'rcpg125B2\n\xf3 hel\t\x00 bw\x05\xb0ld}\n\x80\x0f\xa0')
        # test uncompressed
        self.assertEqual(
            compress(data, compressed=False),
            '7\x00\x00\x00+\x00\x00\x00MELA\x03\xa3n}{\\rtf1\\ansi\\ansicpg'
            '1252\\pard hello world}\r\n')

    def test_compression_repeated_tokens(self):
        """
        Test compression of data with repeated tokens, crossing write position
        """
        data = '{\\rtf1 WXYZWXYZWXYZWXYZWXYZ}'
        self.assertEqual(
            compress(data),
            '\x1a\x00\x00\x00\x1c\x00\x00\x00LZFu\xe2\xd4KQA\x00\x04 WXYZ\r'
            'n}\x01\x0e\xb0')

    def test_hither_and_thither(self):
        """
        Test decompression of compressed data
        """
        data = '{\\rtf1\\ansi\\mac\\deff0\\deftab720'
        self.assertEqual(decompress(compress(data, compressed=True)), data)
        
    def test_hither_and_thither_long(self):
        """
        Test decompression of compressed data larger than 4096
        """
        data = '{\\rtf1\\ansi\\ansicpg1252\\pard hello world'
        while len(data) < 4096:
            data += "testtest"
        data += "}"
        self.assertEqual(decompress(compress(data, compressed=True)), data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
