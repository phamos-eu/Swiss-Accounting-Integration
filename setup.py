# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in swiss_accounting_integration/__init__.py
from swiss_accounting_integration import __version__ as version

setup(
	name='swiss_accounting_integration',
	version=version,
	description='ERPNexts functionality with Swiss QR Integration and Abacus Export',
	author='Grynn',
	author_email='paideepak@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
