# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pybrainyquote']
install_requires = \
['bs4>=0.0.1,<0.0.2',
 'furl>=2.1.0,<3.0.0',
 'lxml>=4.5.1,<5.0.0',
 'requests>=2.23.0,<3.0.0']

setup_kwargs = {
    'name': 'pybrainyquote',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
