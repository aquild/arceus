# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""

setup(
    name="arceus",
    version="1.0.0",
    description="Minecraft name sniper.",
    author="Aquild",
    packages=find_packages(),
    install_requires=[
        "requests",
        "requests-random-user-agent",
        "pythonping",
        "bs4",
        "pause",
        "click",
        "PyInquirer",
        "colorama",
        "termcolor",
        "pyfiglet",
    ],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={"console_scripts": ["arceus=arceus.cli:cli"]},
)
