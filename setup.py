import os
from setuptools import setup
import remoter

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "remoter-py",
    version = remoter.version,
    author = "John Torakis",
    author_email = "john.torakis@gmail.com",
    description = ("A tool for remote enumeration of Linux systems"),
    license = "BSD",
    keywords = "",
    url = "",
    packages=['remoter',],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Security",
        "License :: OSI Approved :: BSD License",
    ],
)