from setuptools import setup, find_packages
from pathlib import Path

long_description = Path('Readme.md').read_text()

setup(
    name='py_shiftmanager',
    version='0.1.1',
    description='A simplified, all-in-one shop for handling multithreading/multiprocessing using a managed queue system.',
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'dill==0.3.6',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
