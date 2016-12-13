from distutils.core import setup

setup(
    name='StructureDB',
    version='1',
    packages=['searcher', 'old_django.stdb', 'old_django.stdb.migrations', 'old_django.StructureDB'],
    url='',
    license='Beerware',
    author='Daniel Kratzert',
    author_email='dkratzert@gmx.de',
    description='A structure database', requires=['PyQt5']
)
