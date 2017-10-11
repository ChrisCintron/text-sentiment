#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# requirements.txt Notes
# Create requirements.txt file command:  pip freeze > requirements.txt
# Install requirements.txt file command:  pip -r install requirements.txt
# Utility function to read REQUIREMENTS.txt inside a virtual env
# Parses requirements.txt into a list of requirements for the install_requires option.
def requires(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        content = f.readlines()
        content = [x.strip() for x in content] #Takes /n off each line
    return content

setup(
    name='text-sentiment',
    version='0.1.0',
    packages=find_packages(exclude=['tests',]),
    install_requires=requires('requirements.txt'), #All modules associated with package
    license='Public Domain',
    long_description=read('README'),
    #url='https://example.com', #To github
    #download_url='https://example.com', #Tarball download
    author='Christopher Cintron',
    author_email='chris.cintron502@gmail.com'
)
