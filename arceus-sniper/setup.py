# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("../README.md").read()
except IOError:
    long_description = ""

setup(
    name="arceus",
    version="2.1.3",
    description="Minecraft name sniper.",
    author="Aquild",
    packages=find_packages(),
    install_requires=[
        "arceus-net",
        "requests",
        "requests-random-user-agent",
        "tcp-latency",
        "bs4",
        "pause",
        "click",
        "PyInquirer",
        "colorama",
        "termcolor",
        "pyfiglet",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={"console_scripts": ["arceus=arceus.cli:cli"]},
)
