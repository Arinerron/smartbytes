#!/usr/bin/env python

import setuptools
from distutils.core import setup

def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(name = 'smartbytes',
      version = '1.4',
      description = 'makes bytes in Python significantly less painful',
      long_description = readme(),
      long_description_content_type="text/markdown",
      author = 'Aaron Esau',
      author_email = 'python@aaronesau.com',
      url = 'https://github.com/Arinerron/smartbytes',
      keywords = 'smartbytes bytes str string bytesarray byte parsing pwntools pwn ctf',
      packages = ['smartbytes'])
