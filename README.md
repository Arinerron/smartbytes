# About

smartbytes makes byte parsing not painful

\*[insert *I can't believe it's not Python 2!* on image](https://images-na.ssl-images-amazon.com/images/G/01/aplusautomation/vendorimages/4bc3e8fe-4c6e-4b72-a676-57a4f0aeb3eb.jpg._CB527652977_.jpg)\*

# Installation

## PyPi

```
# pip3 install smartbytes
```

## Manual

The only requirement for smartbytes is any version of `python3`.

```
$ git clone https://github.com/Arinerron/smartbytes.git
$ cd smartbytes

# sudo python3 setup.py install
```

# Documentation

The best way to document is to just give you a ton of cool examples.

```python
>>> from smartbytes import *

# you can easily concat values to build smartbytes objects

>>> smartbytes('hello world')
b'hello world'

>>> smartbytes('hello') + 0x20 + smartbytes('world')
b'hello world'

>>> smartbytes('hello') + ' ' + b'world'
b'hello world'

# you can search for strings easily

>>> with open('/usr/lib/libc-2.31.so', 'rb') as f:
...     contents = f.read()
... 
>>> smartbytes(contents)['/bin/sh\x00'] # find offset of /bin/sh string in libc
1618243

# smartbytes works with iters

>>> smartbytes(range(10))
b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t'

>>> smartbytes(range(10)) + range(10)
b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\x00\x01\x02\x03\x04\x05\x06\x07\x08\t'

>>> str(smartbytes(range(10)))
'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t'

# it can flatten arrays out too

>>> smartbytes([(2,3),4],[5,(((3,5),),)])
b'\x02\x03\x04\x05\x03\x05'

# there are some cool functions to make your smartbytes usable

>>> value = smartbytes(range(100))
>>> value
b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abc'

>>> str(value)
'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abc'

>>> value.hex()
b'000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f60616263'

>>> print(value.hexdump())
0 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f    ................
10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f    ................
20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f     !"#$%&'()*+,-./
30 31 32 33 34 35 36 37 38 39 3a 3b 3c 3d 3e 3f    0123456789:;<=>?
40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f    @ABCDEFGHIJKLMNO
50 51 52 53 54 55 56 57 58 59 5a 5b 5c 5d 5e 5f    PQRSTUVWXYZ[\]^_
60 61 62 63                                        `abc

# it comes with pwntools-like packing functions
# NOTE: endianness can be specified using kwarg endian (e.g. endian='big')

>>> p8(0x12)
b'\x12'

>>> p16(0xaa)
b'\xaa'

>>> p32(0xdead)
b'\x00\x00\xad\xde'

>>> p64(0xdeadbeef)
b'\x00\x00\x00\x00\x00\x00\xef\xbe\xad\xde'

# ...but it can also do packing and unpacking without fixed sizes

>>> p(0xdeadbeef)
b'\xde\xad\xbe\xef'

>>> u('what does this look like when unpacked')
15202366010688944152837236994529002040902519784461806602639909313811909172211576228574618980

# smartbytes even works with pwntools!

>>> from smartbytes import *
>>> from pwn import *
>>> p = process('cat')
[x] Starting local process '/usr/bin/cat'
[+] Starting local process '/usr/bin/cat': pid 1470268
>>> line = smartbytes(b'robert', 0x20, 'is') + 0x20 + b'an' + smartbytes(' ', 'arch', 0x20, 'user btw')
>>> line
b'robert is an arch user btw'
>>> p.sendline(line)
```
