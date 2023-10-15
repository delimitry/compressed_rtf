#-*- coding: utf8 -*-

import unittest
from compressed_rtf.compressed_rtf import compress, decompress
from compressed_rtf.crc32 import crc32


class Test(unittest.TestCase):
    """
    Test RTF compression and decompression
    """

    def test_decompress(self):
        """
        Test decompression
        """
        data = b'-\x00\x00\x00+\x00\x00\x00LZFu\xf1\xc5\xc7\xa7\x03\x00\n\x00' \
            b'rcpg125B2\n\xf3 hel\t\x00 bw\x05\xb0ld}\n\x80\x0f\xa0'
        self.assertEqual(
            decompress(data),
            b'{\\rtf1\\ansi\\ansicpg1252\\pard hello world}\r\n')
        # test raw decompression
        data = b'.\x00\x00\x00"\x00\x00\x00MELA\x00\x00\x00\x00{\\rtf1\\ansi\\an' \
            b'sicpg1252\\pard test}'
        self.assertEqual(
            decompress(data),
            b'{\\rtf1\\ansi\\ansicpg1252\\pard test}')
        # test < 16 bytes long data exception
        with self.assertRaises(Exception):
            decompress(b'')
        with self.assertRaises(Exception):
            decompress(b'0123456789abcde')
        # test unknown compression type exception
        with self.assertRaises(Exception):
            decompress(b'\x10\x00\x00\x00\x11\x00\x00\x00ABCD\xff\xff\xff\xff')
        # test invalid CRC exception
        with self.assertRaises(Exception):
            decompress(b'\x10\x00\x00\x00\x11\x00\x00\x00LZFu\xff\xff\xff\xff')

    def test_crc32(self):
        """
        Test CRC32 computation
        """
        data = b'\x03\x00\n\x00rcpg125B2\n\xf3 hel\t\x00 bw\x05\xb0ld}\n\x80' \
            b'\x0f\xa0'
        self.assertEqual(crc32(data), 0xa7c7c5f1)
        # test empty crc32
        self.assertEqual(crc32(b''), 0x00000000)

    def test_compression(self):
        """
        Test compression types compressed and uncompressed
        """
        data = b'{\\rtf1\\ansi\\ansicpg1252\\pard hello world}\r\n'
        self.assertEqual(
            compress(data, compressed=True),
            b'-\x00\x00\x00+\x00\x00\x00LZFu\xf1\xc5\xc7\xa7\x03\x00\n\x00'
            b'rcpg125B2\n\xf3 hel\t\x00 bw\x05\xb0ld}\n\x80\x0f\xa0')
        # test uncompressed
        self.assertEqual(
            compress(data, compressed=False),
            b'7\x00\x00\x00+\x00\x00\x00MELA\x00\x00\x00\x00{\\rtf1\\ansi\\ansicpg'
            b'1252\\pard hello world}\r\n')

    def test_compression_repeated_tokens(self):
        """
        Test compression of data with repeated tokens, crossing write position
        """
        data = b'{\\rtf1 WXYZWXYZWXYZWXYZWXYZ}'
        self.assertEqual(
            compress(data),
            b'\x1a\x00\x00\x00\x1c\x00\x00\x00LZFu\xe2\xd4KQA\x00\x04 WXYZ\r'
            b'n}\x01\x0e\xb0')

    def test_hither_and_thither(self):
        """
        Test decompression of compressed data
        """
        data = b'{\\rtf1\\ansi\\mac\\deff0\\deftab720'
        self.assertEqual(decompress(compress(data, compressed=True)), data)

    def test_hither_and_thither_long(self):
        """
        Test decompression of compressed data larger than 4096
        """
        data = b'{\\rtf1\\ansi\\ansicpg1252\\pard hello world'
        while len(data) < 4096:
            data += b'testtest'
        data += b'}'
        self.assertEqual(decompress(compress(data, compressed=True)), data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
