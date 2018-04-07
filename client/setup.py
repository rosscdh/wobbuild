import os
from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'), session=False)
REQUIREMENTS = [str(ir.req) for ir in install_reqs]

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

VERSION = os.getenv('RELEASE_VERSION', '0.0.1')


setup(
    name='wobbuild',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='MIT License',
    description='Wobbuild - Open Source (docker based) Build System',
    long_description=README,
    url='https://github.com/rosscdh/wobbuild',
    author='Ross Crawford-d\'Heureuse',
    author_email='sendrossemail@gmail.com',
    classifiers=[
        'Environment :: CLI',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: DevOps',
        'Topic :: Internet :: DevOps :: Build Systems',
    ],
    entry_points={'console_scripts': [
        'wobbuild = wobbuild.main:wobbuild',
    ], },
)