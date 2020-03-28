#!/usr/bin/env python3

from smartbytes import *

a = smartbytes('hello world')
assert a.hex().unhex() == a
a.hexdump(columns = 8, content = True)
