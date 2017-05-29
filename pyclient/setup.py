from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='0-rest-api',
    version='1.1.0.a',
    description='G8OS resource pool client',
    long_description=long_description,
    url='https://github.com/g8os/grid',
    author='Christophe de Carvalho',
    author_email='christophe@gig.tech',
    license='Apache 2.0',
    packages=find_packages(),
    namespace_packages=['zeroos'],
    install_requires=['python-dateutil', 'Jinja2'],
)
