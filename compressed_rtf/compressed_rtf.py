# -*- coding: utf8 -*-
"""
Compressed Rich Text Format (RTF) worker

Based on Rich Text Format (RTF) Compression Algorithm
https://msdn.microsoft.com/en-us/library/cc463890(v=exchg.80).aspx
"""

import struct
import sys
from io import BytesIO
from .crc32 import crc32

__all__ = ['compress', 'decompress']

PY3 = sys.version_info[0] == 3

INIT_DICT = (
    b'{\\rtf1\\ansi\\mac\\deff0\\deftab720{\\fonttbl;}{\\f0\\fnil \\froman \\'
    b'fswiss \\fmodern \\fscript \\fdecor MS Sans SerifSymbolArialTimes New '
    b'RomanCourier{\\colortbl\\red0\\green0\\blue0\r\n\\par \\pard\\plain\\'
    b'f0\\fs20\\b\\i\\u\\tab\\tx'
)

INIT_DICT_SIZE = 207
MAX_DICT_SIZE = 4096

COMPRESSED = b'LZFu'
UNCOMPRESSED = b'MELA'


def char_to_int(val):
    """Convert a character to its ordinal value."""
    return ord(val) if PY3 else val


def compress(data, compressed=True):
    """
    Compress `data` using RTF compression algorithm
    If `compressed` flag is False, data will be written uncompressed
    """
    output_buffer = b''
    # set init dict
    init_dict = list(INIT_DICT + b' ' * (MAX_DICT_SIZE - INIT_DICT_SIZE))
    write_offset = INIT_DICT_SIZE
    # compressed
    if compressed:
        comp_type = COMPRESSED
        # make stream
        in_stream = BytesIO(data)
        # init params
        control_byte = 0
        control_bit = 1
        token_offset = 0
        token_buffer = b''
        while True:
            # find the longest match
            dict_offset, longest_match, write_offset = \
                _find_longest_match(init_dict, in_stream, write_offset)
            char = in_stream.read(longest_match if longest_match > 1 else 1)
            # EOF input stream
            if not char:
                # update params
                control_byte |= 1 << control_bit - 1
                control_bit += 1
                token_offset += 2
                # add dict reference
                dict_ref = (write_offset & 0xfff) << 4
                token_buffer += struct.pack('>H', dict_ref)
                # add to output
                output_buffer += struct.pack('B', control_byte)
                output_buffer += token_buffer[:token_offset]
                break
            if longest_match > 1:
                # update params
                control_byte |= 1 << control_bit - 1
                control_bit += 1
                token_offset += 2
                # add dict reference
                dict_ref = (dict_offset & 0xfff) << 4 | (
                        longest_match - 2) & 0xf
                token_buffer += struct.pack('>H', dict_ref)
            else:
                # character is not found in dictionary
                if longest_match == 0:
                    init_dict[write_offset] = char_to_int(char)
                    write_offset = (write_offset + 1) % MAX_DICT_SIZE
                # update params
                control_byte |= 0 << control_bit - 1
                control_bit += 1
                token_offset += 1
                # add literal
                token_buffer += char
            if control_bit > 8:
                # add to output
                output_buffer += struct.pack('B', control_byte)
                output_buffer += token_buffer[:token_offset]
                # reset params
                control_byte = 0
                control_bit = 1
                token_offset = 0
                token_buffer = b''
        crc_value = struct.pack('<I', crc32(output_buffer))
    else:
        # if uncompressed - copy data to output
        comp_type = UNCOMPRESSED
        output_buffer = data
        crc_value = struct.pack('<I', 0x00000000)
    # write compressed RTF header
    comp_size = struct.pack('<I', len(output_buffer) + 12)
    raw_size = struct.pack('<I', len(data))
    return comp_size + raw_size + comp_type + crc_value + output_buffer


def decompress(data):
    """
    Decompress `data` using RTF compression algorithm
    """
    # set init dict
    init_dict = list(INIT_DICT)
    init_dict += list(b' ' * (MAX_DICT_SIZE - INIT_DICT_SIZE))
    if len(data) < 16:
        raise Exception('Data must be at least 16 bytes long')  # pylint: disable=broad-exception-raised
    write_offset = INIT_DICT_SIZE
    output_buffer = BytesIO()
    # make stream
    in_stream = BytesIO(data)

    # read compressed RTF header
    comp_size = struct.unpack('<I', in_stream.read(4))[0]
    raw_size = struct.unpack('<I', in_stream.read(4))[0]
    comp_type = in_stream.read(4)
    crc_value = struct.unpack('<I', in_stream.read(4))[0]

    # get only data
    contents = BytesIO(in_stream.read(comp_size - 12))

    if comp_type == COMPRESSED:
        # check CRC
        if crc_value != crc32(contents.read()):
            raise Exception('CRC is invalid! The file is corrupt!')  # pylint: disable=broad-exception-raised
        contents.seek(0)
        end = False
        while not end:
            val = contents.read(1)
            if not val:
                break
            control = '{0:08b}'.format(ord(val))  # pylint: disable=consider-using-f-string
            # check bits from LSB to MSB
            for i in range(1, 9):
                if control[-i] == '1':
                    # token is reference (16 bit)
                    val = contents.read(2)
                    if not val:
                        break
                    token = struct.unpack('>H', val)[0]  # big-endian
                    # extract [12 bit offset][4 bit length]
                    offset = (token >> 4) & 0b111111111111
                    length = token & 0b1111
                    # end indicator
                    if write_offset == offset:
                        end = True
                        break
                    actual_length = length + 2
                    for step in range(actual_length):
                        read_offset = (offset + step) % MAX_DICT_SIZE
                        char = init_dict[read_offset]
                        if PY3:
                            output_buffer.write(bytes([char]))
                        else:
                            output_buffer.write(char)
                        init_dict[write_offset] = char
                        write_offset = (write_offset + 1) % MAX_DICT_SIZE
                else:
                    # token is literal (8 bit)
                    val = contents.read(1)
                    if not val:
                        break
                    output_buffer.write(val)
                    init_dict[write_offset] = ord(val) if PY3 else val
                    write_offset = (write_offset + 1) % MAX_DICT_SIZE
    elif comp_type == UNCOMPRESSED:
        # check CRC
        if crc_value != 0x00000000:
            raise Exception('CRC is invalid! Must be 0x00000000!')  # pylint: disable=broad-exception-raised
        return contents.read(raw_size)
    else:
        raise Exception('Unknown type of RTF compression!')  # pylint: disable=broad-exception-raised
    return output_buffer.getvalue()


def _find_longest_match(init_dict, stream, write_offset):
    """
    Find the longest match
    """
    # read the first char
    char = stream.read(1)
    if not char:
        return 0, 0, write_offset
    prev_write_offset = write_offset
    dict_index = 0
    match_len = 0
    longest_match_len = 0
    dict_offset = 0
    # find the first char
    while True:
        if init_dict[dict_index % MAX_DICT_SIZE] == char_to_int(char):
            match_len += 1
            # if found the longest match
            if longest_match_len < match_len <= 17:
                dict_offset = dict_index - match_len + 1
                # add to dictionary and update the longest match
                init_dict[write_offset] = char_to_int(char)
                write_offset = (write_offset + 1) % MAX_DICT_SIZE
                longest_match_len = match_len
            # read the next char
            char = stream.read(1)
            if not char:
                stream.seek(stream.tell() - match_len, 0)
                return dict_offset, longest_match_len, write_offset
        else:
            stream.seek(stream.tell() - match_len - 1, 0)
            match_len = 0
            # read the first char
            char = stream.read(1)
            if not char:
                break
        dict_index += 1
        if dict_index >= prev_write_offset + longest_match_len:
            break
    stream.seek(stream.tell() - match_len - 1, 0)
    return dict_offset, longest_match_len, write_offset
