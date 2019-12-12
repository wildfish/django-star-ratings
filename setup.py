import os
import re
import shutil
import sys
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search('__version__ = [\'"]([^\'"]+)[\'"]', init_py).group(1)


version = get_version('star_ratings')

if sys.argv[-1] == 'publish':
    if os.system('pip freeze | grep wheel'):
        print('wheel not installed.\nUse `pip install wheel`.\nExiting.')
        sys.exit()
    if os.system('pip freeze | grep twine'):
        print('twine not installed.\nUse `pip install twine`.\nExiting.')
        sys.exit()
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    print('You probably want to also tag the version now:')
    print('  git tag -a {} -m \'version {}\''.format(version, version))
    print('  git push --tags')
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('django_star_ratings.egg-info')
    sys.exit()

setup(
    name='django-star-ratings',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'star_ratings/static': ['*'],
        'star_ratings/templates': ['*'],
        '': ['README.rst', 'setup.cfg'],
    },
    exclude_package_data={
        '': ['__pycache__', '*.py[co]'],
        'star_ratings/static/star_ratings/js/node_modules': ['*'],
    },
    license='BSD License',
    description=('A Django app to add star ratings to models.'),
    long_description=README,
    url='https://github.com/wildfish/django-star-ratings',
    author='Wildfish',
    author_email='developers@wildfish.com',
    keywords='ratings',
    install_requires=[
        'django',
        'django-model-utils',
        'django-braces',
        'swapper',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
