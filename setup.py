# Tim Lee
# leetimone@gmail.com

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'File backup program',
    'author': 'Tim Lee',
    'url': 'https://github.com/TimboTambo/BackItUp',
    'download_url': 'git@github.com:TimboTambo/BackItUp.git',
    'author_email': 'leetimone@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'BackItUp'
}

setup(**config)
