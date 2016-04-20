"""Setup script for governor."""
from setuptools import setup
import codecs
import os
import sys
import re

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Return multiple read calls to different readable objects as a single
    string."""
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(HERE, *parts), 'r').read()


def find_version(*file_paths):
    """Find the "__version__" string in files on *file_path*."""
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

LONG_DESCRIPTION = read('README.md')

setup(
    name='governor',
    version=find_version('governor', '__init__.py'),
    url='https://github.com/compose/governor',
    license='MIT License',
    author='Compose',
    install_requires=[
        'psycopg2',
        'pyyaml'
        ],
    description='A Template for PostgreSQL HA with etcd',
    long_description=LONG_DESCRIPTION,
    entry_points={
        'console_scripts': [
            'governor = scripts.governorctl:main',
            ],
        },
    packages=['governor', 'governor.helpers', 'scripts'],
    include_package_data=True,
    package_data={'governor.helpers': ['helpers/*.py']},
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'nvironment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        ],
)
