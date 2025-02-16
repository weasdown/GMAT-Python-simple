# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='gmat_py_simple',
    version='0.4.0',
    description='An extra wrapper for the GMAT Python API to simplify setting up mission simulations.',
    long_description=readme,
    author='William Easdown Babb',
    url='https://github.com/weasdown/GMAT-Python-simple',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)