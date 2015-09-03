import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="wildfish-ratings",
    version="0.1.0",
    author="Wildfish",
    author_email="rolo@wildfish.com",
    description=("Django ratings"),
    license="BSD",
    keywords="ratings",
    url="https://github.com/wildfish/wildfish-ratings",
    packages=find_packages(),
    long_description=read('README.md'),
    include_package_data=True,
    install_requires=[
        "Django >= 1.6, <= 1.8.4",
        "django-model-utils",
        "django-braces"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License"
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
)
