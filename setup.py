import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-star-ratings',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description=('A Django app to add star ratings to models.'),
    long_description=README,
    url='https://github.com/wildfish/star-ratings',
    author='Wildfish',
    author_email='developers@wildfish.com',
    keywords='ratings',
    install_requires=[
        'Django >= 1.7, <= 1.8.4',
        'django-model-utils',
        'django-braces'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
