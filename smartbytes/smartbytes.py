#!/usr/bin/env python3
#
# smartbytes: makes parsing bytes ez
#
# Author: Aaron Esau <python@aaronesau.com>
# License: MIT (see LICENSE.md)


import sys, binascii, struct, itertools, logging, string, builtins, base64


# functions to use from package


__all__ = ['smartbytes', 'smartbytesiter', 'to_bytes', 'u', 'u8', 'u16', 'u32', 'u64', 'p', 'p8', 'p16', 'p32', 'p64', 'e', 'E', 'sb']


# in case builtins gets overriden, we want the object as an alternate name


_bytes = bytes
_str = str


# setup logging


# XXX: should we add this by default?
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler(sys.stdout))


# encoding functions


def hexify(x, endian = 'big', encoding = None):
    if not encoding:
        f = lambda y : y
        if E(endian) == 'little':
            f = reversed

        return smartbytes(''.join(f([hex(x)[2:].zfill(2) for x in to_bytes(x)]))).get_content()
    else:
        return binascii.hexlify(to_bytes(x, endian = endian, encoding = encoding))

unhexify = lambda x, endian = 'big', encoding = 'latin1' : binascii.unhexlify(to_bytes(x, endian = endian, encoding = encoding))


# parsing functions


'''
converts any type to bytes
'''
def to_bytes(value, endian = 'big', encoding = 'latin1'):
    if isinstance(value, bytearray):
        return bytes(value)
    elif isinstance(value, _bytes):
        return value
    elif isinstance(value, smartbytes):
        return value.get_contents()
    elif isinstance(value, _str):
        return value.encode(encoding)
    elif isinstance(value, int):
        return _bytes(p(value, endian = endian, signed = False))
    elif '__iter__' in dir(value):
        return b''.join([to_bytes(x) for x in value])

    log.warning('warning: cannot convert value %s of type %s to bytes' % (_str(value), type(value)))

    raise TypeError


# packing functions

'''
converts 'little' -> '<' and 'big' -> '>'
'''
e = lambda endian : ('<' if endian.strip().lower() in ['<', 'little'] else '>')

'''
converts '<' -> 'little' and '>' -> 'big'
'''
E = lambda endian : ('little' if endian.strip().lower() in ['<', 'little'] else 'big')

ul = lambda n : lambda x, endian = '>' : struct.unpack(e(endian) + n, _bytes(smartbytes(x)))[0]
pl = lambda n : lambda x, endian = '>' : smartbytes(struct.pack(e(endian) + n, x))

u8 = ul('b')
u16 = ul('H')
u32 = ul('I')
u64 = ul('Q')

p8 = pl('b')
p16 = pl('H')
p32 = pl('I')
p64 = pl('Q')

'''
unpacks any type to int
'''
u = lambda data, endian = 'big', signed = False : int.from_bytes(_bytes(to_bytes(data)), byteorder = endian, signed = signed)

'''
packs any type to smartbytes
'''
# p = lambda n, size = None, endian = 'big', signed = False : smartbytes(n.to_bytes(((n.bit_length() // 8) + 1 if size is None else size), byteorder = endian, signed = signed))
p = lambda n, size = None, endian = 'big', signed = False : smartbytes(n.to_bytes((
    (((n.bit_length() - 1) // 8) + 1 if n != 0 else 1)
if size is None else size), byteorder = endian, signed = signed))


# smartbytes classes


class smartbytesiter:
    def __init__(self, array):
        self.array = array
        self.index = 0

        l = self.__lambda__

        self.next8 = l(1, direction = self.next)
        self.next16 = l(2, direction = self.next)
        self.next32 = l(4, direction = self.next)
        self.next64 = l(8, direction = self.next)

        self.prev8 = l(1, direction = self.prev)
        self.prev16 = l(2, direction = self.prev)
        self.prev32 = l(4, direction = self.prev)
        self.prev64 = l(8, direction = self.prev)

        self.back8 = l(1, direction = self.prev, default_offset = False)
        self.back16 = l(2, direction = self.prev, default_offset = False)
        self.back32 = l(4, direction = self.prev, default_offset = False)
        self.back64 = l(8, direction = self.prev, default_offset = False)

    def __lambda__(self, size, direction, default_offset = True):
        return lambda offset = default_offset : direction(size = size, offset = offset)

    def __iter__(self):
        return self

    # generic movement functions

    def next(self, size = 1, offset = True):
        return self.__next__(size, offset)

    def __next__(self, size = 1, offset = True, except_end = True):
        retval = smartbytes(self.array.get_contents()[self.index : self.index + size])

        if offset:
            self.index += size

        if except_end and self.index > len(self.array):
            raise StopIteration

        return retval

    def prev(self, size = 1, offset = False):
        return self.__prev__(size, offset)

    def previous(self, size = 1, offset = False):
        return self.__prev__(size, offset)

    def back(self, size = 1, offset = True):
        return self.__prev__(size, offset)

    def __prev__(self, size = 1, offset = True):
        retval = smartbytes(self.array.get_contents()[self.index - size : self.index])

        if offset:
            self.index -= size

        return retval

    # misc functions

    def set_index(self, index):
        self.index = index
        return self

    def get_index(self):
        return self.index


class smartbytes(_bytes):
    def __new__(cls, *args, **kwargs):
        return _bytes.__new__(cls)

    def __init__(self, *contents, **kwargs):
        if isinstance(contents, tuple):
            contents = list(contents)
        if len(contents) == 1:
            contents = contents[0]

        self.contents = self._to_bytes(contents)

    # adding bytes

    def __add__(self, value):
        return smartbytes(self).add(value)

    def add(self, value, encoding = 'latin1'):
        return smartbytes(self).append(value, encoding = encoding)

    def __mul__(self, value):
        try:
            return smartbytes(self.get_contents() * value)
        except TypeError as e:
            raise e

    def __rmul__(self, value):
        return self.__mul__(value)

    def multiply(self, value):
        return self.__mul__(value)

    def _to_bytes(self, value, endian = 'big', encoding = 'latin1'):
        if isinstance(value, smartbytes):
            return value.get_contents()

        return to_bytes(value, endian = endian, encoding = encoding)

    def append(self, value, encoding = 'latin1'):
        self.contents += self._to_bytes(value, encoding = encoding)

        return self

    # getting values

    def get_content(self):
        return self.get_contents()

    def get_contents(self):
        return self.contents

    def encode(self, *args, **kwargs):
        return to_bytes(self, *args, **kwargs)

    def decode(self, encoding = None):
        return self.__str__(encoding = encoding)

    def bytes(self, **kwargs):
        return bytes(self, **kwargs)

    def as_bytes(self, **kwargs):
        return self.bytes(**kwargs)

    def to_bytes(self, **kwargs):
        return self.bytes(**kwargs)

    def str(self, **kwargs):
        return str(self, **kwargs)

    def as_str(self, **kwargs):
        return self.str(**kwargs)

    def to_str(self, **kwargs):
        return self.str(**kwargs)

    def as_human(self):
        return self.human()

    def to_human(self):
        return self.human()

    def as_hexdump(self, *args, **kwargs):
        return self.hexdump(*args, **kwargs)

    def to_hexdump(self, *args, **kwargs):
        return self.hexdump(*args, **kwargs)

    def repr(self):
        return repr(self)

    def as_repr(self):
        return self.repr()

    def to_repr(self):
        return self.repr()

    def __str__(self, encoding = None):
        if encoding:
            return self.get_contents().decode(encoding = encoding)
        else:
            return ''.join(chr(x) for x in self.get_contents())

    def __bytes__(self):
        return self.get_contents()

    def __human__(self):
        return _str(_bytes(self))[1:]

    def __repr__(self):
        return 'sb' + self.get_contents().__repr__()[1:]

    def __eq__(self, value):
        return self.get_contents() == smartbytes(value).get_contents()

    def hexdump(self, columns = 16, content = True):
        build = smartbytes()
        tmp = smartbytes()

        for i in range(len(self)):
            build += self[i].hex()
            tmp += self[i]

            if columns and (i + 1) % columns == 0:
                if content:
                    build += b'    '
                    build += ''.join([_str(x) if (_str(x) in string.printable and not _str(x) in '\t\n\r\x0b\x0c') else '.' for x in tmp])
                    tmp = smartbytes()

                build += b'\n'
            else:
                build += b' '

        if tmp and content:
            build += b'   ' * (columns - len(tmp)) + b'   '
            build += tmp


        return build

    def hex(self, endian = 'big', zero_pad = True):
        retval = hexify(self.get_contents(), endian = endian)
        if zero_pad and len(retval) % 2: # 0 pad
            return smartbytes('0', retval)
        return smartbytes(retval)

    def unhex(self):
        val = self.get_contents()
        if len(val) % 2 != 0:
            val = b'0' + val
        return smartbytes(unhexify(val))

    def base64(self):
        return smartbytes(base64.b64encode(self.get_contents()))

    def unbase64(self):
        return smartbytes(base64.b64decode(self.get_contents()))

    def human(self):
        return self.__human__()

    def join(self, values):
        build = smartbytes()

        iterator = iter(values)
        nextval = None

        try:
            while True:
                add_space = not nextval is None
                nextval = next(iterator)

                if add_space:
                    build += self

                build += nextval
        except StopIteration:
            return build

    def chunks(self, chunk_size, join_with = None):
        chunks = [self[i:i+chunk_size] for i in range(0, len(self), chunk_size)]

        if join_with == None:
            return chunks
        else:
            return smartbytes(join_with).join(chunks)

    def as_chunks(self, *args, **kwargs):
        return self.chunks(*args, **kwargs)

    def chunkify(self, chunk_size):
        return self.chunkify(chunk_size)

    # string-like operations

    def ljust(self, amount, char = b'\x00'):
        return smartbytes(self.get_contents().ljust(amount, self._to_bytes(char)))

    def rjust(self, amount, char = b'\x00'):
        return smartbytes(self.get_contents().rjust(amount, self._to_bytes(char)))

    def zfill(self, length):
        return smartbytes(self.get_contents().rjust(length, '0'))

    def startswith(self, prefix):
        return self.get_contents().startswith(self._to_bytes(prefix))

    def endswith(self, suffix):
        return self.get_contents().endswith(self._to_bytes(suffix))

    def replace(self, char, withchar, count = -1):
        return smartbytes(self.get_contents().replace(self._to_bytes(char), self._to_bytes(withchar), count))

    def remove(self, char, count = -1):
        return self.replace(char, '', count = count)

    def split(self, char, count = -1):
        return [smartbytes(x) for x in self.get_contents().split(self._to_bytes(char), count)]

    def rsplit(self, char, count = -1):
        return [smartbytes(x) for x in self.get_contents().rsplit(self._to_bytes(char), count)]

    def partition(self, char):
        return tuple(self.split(char, 1))

    def rpartition(self, char):
        return tuple(self.rsplit(char, 1))

    def upper(self):
        return smartbytes(self.get_contents().upper())

    def lower(self):
        return smartbytes(self.get_contents().lower())

    def title(self):
        return smartbytes(self.get_contents().title())

    def strip(self, *kargs):
        return smartbytes(self.get_contents().strip(*kargs))

    def lstrip(self, *kargs):
        return smartbytes(self.get_contents().lstrip(*kargs))

    def rstrip(self, *kargs):
        return smartbytes(self.get_contents().rstrip(*kargs))

    # iterating the array

    def __iter__(self):
        return smartbytesiter(self)

    def iter(self):
        return self.__iter__()

    # misc operations

    def __len__(self):
        return len(self.get_contents())

    def __contains__(self, key):
        return self[smartbytes(key)] != -1

    def contains(self, key):
        return key in self

    def __reversed__(self):
        return smartbytes(reversed(self.get_contents()))

    def reverse(self):
        return self.__reversed__()

    def find(self, key, *args, **kwargs):
        key = smartbytes(key)
        return self.get_contents().find(key.get_contents(), *args, **kwargs)

    def rfind(self, key, *args, **kwargs):
        key = smartbytes(key)
        return self.get_contents().find(key.get_contents(), *args, **kwargs)

    def __getitem__(self, key, *args, **kwargs):
        try:
            # try as int
            return smartbytes(self.get_contents().__getitem__(key, *args, **kwargs))
        except TypeError:
            # ok, we're searching
            return self.find(key, *args, **kwargs)

    def __setitem__(self, key, value, length = None):
        try:
            self.contents = bytes(self[0:key] + smartbytes(value) + self[key+1+(0 if length == None else length):len(self)])
        except TypeError:
            # find the string (let's assume it's one) and replace at that index instead
            self.__setitem__(self[key], value, length = (len(key) if length == None else length))

    def insert(self, key, value, length = -1):
        self.__setitem__(key, value, length = length)


# shorthand


sb = smartbytes

#builtins.bytes = sb
# although this does work ^ and is cool, it will break code:
# >>> bytes('adsf', 234234)
# sb'adsf\x03\x92\xfa'
# >>> bytes('asdf', 'utf-8')
# sb'asdfutf-8'
