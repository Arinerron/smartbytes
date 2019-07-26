# About

smartbytes makes byte parsing not painful

\*[insert *I can't believe it's not Python 2!* on image](https://images-na.ssl-images-amazon.com/images/G/01/aplusautomation/vendorimages/4bc3e8fe-4c6e-4b72-a676-57a4f0aeb3eb.jpg._CB527652977_.jpg)\*

# Installation

The only requirement for smartbytes is any version of `python3`.

```
git clone https://github.com/Arinerron/smartbytes.git
cd smartbytes

sudo python3 setup.py install
```

# Documentation

Coming soon.

# Examples

**_tl;dr_** smartbytes makes it so that
* you can use normal string functions on bytes
* packing and unpacking is easy
* it is trivial to encode/decode in hex
* you can parse bytes in chunks rather than one byte at a time

```
>>> from smartbytes import *

>>> smartbytes('hello world')
b'hello world'

>>> smartbytes('hello') + smartbytes(' world')
b'hello world'

>>> smartbytes('hello') + 0x20 + smartbytes('world')
b'hello world'

>>> smartbytes('hello') + ' ' + b'world'
b'hello world'

>>> smartbytes(0x41) + 'A' + b'A' + 0x41
b'AAAA'

>>> smartbytes(range(10))
b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t'

>>> smartbytes(range(10)) + range(10)
b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\x00\x01\x02\x03\x04\x05\x06\x07\x08\t'

>>> str(smartbytes(range(10)))
'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t'

>>> smartbytes(range(20)).hex()
b'000102030405060708090a0b0c0d0e0f10111213'

>>> print(smartbytes(range(20)).hexdump())
00 01 02 03 04 05 06 07
08 09 0a 0b 0c 0d 0e 0f
10 11 12 13 

>>> p8(0x12)
b'\x12'

>>> p16(0x34)
b'\x004'

>>> p32(0x1234)
b'\x00\x00\x124'

>>> p64(0x1234)
b'\x00\x00\x00\x00\x00\x00\x124'

>>> p(0x12345)
b'\x01#E'

>>> p(0x1234567890)
b'\x124Vx\x90'
```
