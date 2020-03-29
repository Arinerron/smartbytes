#!/usr/bin/env python3
# 
# smartbytes: makes parsing bytes ez
# 
# Author: Aaron Esau <python@aaronesau.com>
# License: MIT (see LICENSE.md)


import sys, binascii, struct, itertools, logging, string


# functions to use from package


__all__ = ['smartbytes', 'smartbytesiter', 'to_bytes', 'u', 'u8', 'u16', 'u32', 'u64', 'p', 'p8', 'p16', 'p32', 'p64', 'e', 'E']


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

unhexify = lambda x, endian = 'big', encoding = 'utf-8' : binascii.unhexlify(to_bytes(x, endian = endian, encoding = encoding))

hexdump = lambda value, columns = 8 : b'\n'.join([b' '.join([b' ' * 2 if a is None else hexify(bytes([a])).rjust(2, b'0') for a in x]) for x in map(lambda *c : tuple(c), *(itertools.chain(iter(to_bytes(value)), [None] * (columns - 1)),) * columns)]).decode() # sorry about this, it was just a challenge for myself


# parsing functions

'''
converts any type to bytes
'''
def to_bytes(value, endian = 'big', encoding = 'utf-8'):
    if isinstance(value, bytearray):
        return bytes(value)
    elif isinstance(value, bytes):
        return value
    elif isinstance(value, smartbytes):
        return value.get_contents()
    elif isinstance(value, str):
        return value.encode(encoding)
    elif isinstance(value, int):
        return bytes(p(value, endian = endian, signed = False))
    elif '__iter__' in dir(value):
        return b''.join([to_bytes(x) for x in value])

    log.warning('warning: cannot convert value %s of type %s to bytes' % (str(value), type(value)))

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

ul = lambda n : lambda x, endian = '>' : struct.unpack(e(endian) + n, bytes(smartbytes(x)))[0]
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
u = lambda data, endian = 'big', signed = False : int.from_bytes(bytes(to_bytes(data)), byteorder = endian, signed = signed)

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


class smartbytes(str):
    def __init__(self, *contents):
        super(str, self).__init__()

        if isinstance(contents, tuple):
            contents = list(contents)
        if len(contents) == 1:
            contents = contents[0]

        self.contents = self._to_bytes(contents)

    # adding bytes

    def __add__(self, value):
        return smartbytes(self).add(value)

    def add(self, value, encoding = 'utf-8'):
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

    def _to_bytes(self, value, endian = 'big', encoding = 'utf-8'):
        if isinstance(value, smartbytes):
            return value.get_contents()

        return to_bytes(value, endian = endian, encoding = encoding)

    def append(self, value, encoding = 'utf-8'):
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

    def __str__(self, encoding = None):
        if encoding:
            return self.get_contents().decode(encoding = encoding)
        else:
            return ''.join(chr(x) for x in self.get_contents())

    def __bytes__(self):
        return self.get_contents()

    def __human__(self):
        return str(bytes(self))[1:]

    def __repr__(self):
        return self.get_contents().__repr__()

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
                    build += ''.join([str(x) if (str(x) in string.printable and not str(x) in '\t\n\r\x0b\x0c') else '.' for x in tmp])
                    tmp = smartbytes()

                build += b'\n'
            else:
                build += b' '

        if tmp and content:
            build += b'   ' * (columns - len(tmp)) + b'   '
            build += tmp


        return build

    def hex(self):
        return smartbytes(hexify(self.get_contents()))

    def unhex(self):
        return smartbytes(unhexify(self.get_contents()))

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

    def chunks(self, chunk_size):
        return [self[i:i+chunk_size] for i in range(0, len(self), chunk_size)]

    def as_chunks(self, chunk_size):
        return self.chunks(chunk_size)

    def chunkify(self, chunk_size):
        return self.chunkify(chunk_size)

    # string-like operations

    def ljust(self, amount, char = b'\x00'):
        return smartbytes(self).get_contents().ljust(amount, self._to_bytes(char))

    def rjust(self, amount, char = b'\x00'):
        return smartbytes(self).get_contents().rjust(amount, self._to_bytes(char))
    
    def startswith(self, prefix):
        return self.get_contents().startswith(self._to_bytes(prefix))

    def endswith(self, suffix):
        return self.get_contents().endswith(self._to_bytes(suffix))

    def replace(self, char, withchar, count = -1):
        return smartbytes(self).get_contents().replace(self._to_bytes(char), self._to_bytes(withchar), count)

    def split(self, char, count = -1):
        return [smartbytes(x) for x in self.get_contents().split(self._to_bytes(char), count)]

    def rsplit(self, char, count = -1):
        return [smartbytes(x) for x in self.get_contents().rsplit(self._to_bytes(char), count)]

    def partition(self, char):
        return tuple(self.split(char, 1))

    def rpartition(self, char):
        return tuple(self.rsplit(char, 1))

    # iterating the array

    def __iter__(self):
        return smartbytesiter(self)
    
    # misc operations

    def __len__(self):
        return len(self.get_contents())

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


# override some common str functions
# XXX: this only works for functions which only take str/bytes args

attrs = [
    'title',
    'lower',
    'upper',
    'translate',
    'zfill',
    'strip',
    'lstrip',
    'rstrip'
]

for attr in attrs:
    attr_func = lambda *args, **kwargs : smartbytes(getattr(str, attr)(*args, **kwargs))
    setattr(smartbytes, attr, attr_func)

del attrs
