from distutils.core import setup

from setuptools import find_packages

setup(
    name='StructureDB',
    version='1',
    packages=find_packages('./', exclude=['CifFile']),
    #['apex', 'displaymol', 'lattice', 'pg8000', 'pymatgen', 'searcher'],
    url='',
    license='Beerware',
    author='Daniel Kratzert',
    author_email='dkratzert@gmx.de',
    description='A structure database',
    requires=['PyQt5', 'numpy'],
    #python_requires='>=3.4',
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    package_data={
        'icon': ['./images/strf.ico'],
        'main': ['strf.py', 'strf_main.ui']
    }
    #py_modules=["strf.py"]
)
